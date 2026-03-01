import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import UploadForm from '../../../features/process/components/UploadForm'

vi.mock('../../../lib/api-client', () => ({
  submitProcessRequest: vi.fn(async () => ({
    status: 'success',
    request_id: 'req_test',
    data: { message: 'validation-passed-ocr-pending', job_id: null }
  }))
}))

import { submitProcessRequest } from '../../../lib/api-client'

function renderWithClient(ui) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

describe('UploadForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  afterEach(() => {
    cleanup()
  })

  it('shows primary take photo and secondary upload actions', () => {
    renderWithClient(<UploadForm />)

    expect(screen.getByRole('button', { name: /take photo/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/upload image/i)).toBeInTheDocument()
  })

  it('submits to process endpoint through api client', async () => {
    const user = userEvent.setup()
    renderWithClient(<UploadForm />)
    const form = screen.getByRole('form', { name: /process-upload-form/i })

    const file = new File(['img-bytes'], 'test.jpg', { type: 'image/jpeg' })
    await user.upload(screen.getByLabelText(/upload image/i), file)
    await user.click(within(form).getByRole('button', { name: /submit/i }))

    expect(submitProcessRequest).toHaveBeenCalledTimes(1)
    expect(await screen.findByText(/request path confirmed/i)).toBeInTheDocument()
  })

  it('shows actionable guidance when validation fails', async () => {
    submitProcessRequest.mockRejectedValueOnce(
      Object.assign(new Error('bad image'), { code: 'image_decode_failed' })
    )

    const user = userEvent.setup()
    renderWithClient(<UploadForm />)
    const form = screen.getByRole('form', { name: /process-upload-form/i })

    const file = new File(['bad-bytes'], 'bad.png', { type: 'image/png' })
    await user.upload(screen.getByLabelText(/upload image/i), file)
    await user.click(within(form).getByRole('button', { name: /submit/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not read that image/i)
  })

  it('shows progress state while valid upload is being processed', async () => {
    let release
    submitProcessRequest.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          release = resolve
        })
    )

    const user = userEvent.setup()
    renderWithClient(<UploadForm />)
    const form = screen.getByRole('form', { name: /process-upload-form/i })

    const file = new File(['img-bytes'], 'test.jpg', { type: 'image/jpeg' })
    await user.upload(screen.getByLabelText(/upload image/i), file)
    await user.click(within(form).getByRole('button', { name: /submit/i }))

    expect(await screen.findByText(/uploading image/i)).toBeInTheDocument()

    release({
      status: 'success',
      request_id: 'req_progress',
      data: { message: 'validation-passed-ocr-pending', job_id: null }
    })

    await waitFor(() => {
      expect(screen.getByText(/valid image accepted/i)).toBeInTheDocument()
    })
  })

  it('shows fallback error message for unrecognised validation code', async () => {
    submitProcessRequest.mockRejectedValueOnce(
      Object.assign(new Error('An unexpected server error occurred'), { code: 'internal_server_error' })
    )

    const user = userEvent.setup()
    renderWithClient(<UploadForm />)
    const form = screen.getByRole('form', { name: /process-upload-form/i })

    const file = new File(['img-bytes'], 'test.jpg', { type: 'image/jpeg' })
    await user.upload(screen.getByLabelText(/upload image/i), file)
    await user.click(within(form).getByRole('button', { name: /submit/i }))

    // code not in validationGuidanceByCode → falls back to error.message
    expect(await screen.findByRole('alert')).toHaveTextContent(/unexpected server error occurred/i)
  })
})
