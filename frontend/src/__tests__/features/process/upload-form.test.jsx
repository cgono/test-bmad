import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import UploadForm from '../../../features/process/components/UploadForm'

vi.mock('../../../lib/api-client', () => ({
  submitProcessRequest: vi.fn(async () => ({
    status: 'success',
    request_id: 'req_test',
    payload: { message: 'ok', job_id: null }
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
  it('shows primary take photo and secondary upload actions', () => {
    renderWithClient(<UploadForm />)

    expect(screen.getByRole('button', { name: /take photo/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/upload image/i)).toBeInTheDocument()
  })

  it('submits to process endpoint through api client', async () => {
    const user = userEvent.setup()
    renderWithClient(<UploadForm />)

    const file = new File(['img-bytes'], 'test.jpg', { type: 'image/jpeg' })
    await user.upload(screen.getByLabelText(/upload image/i), file)
    await user.click(screen.getByRole('button', { name: /submit/i }))

    expect(submitProcessRequest).toHaveBeenCalledTimes(1)
    expect(await screen.findByText(/request path confirmed/i)).toBeInTheDocument()
  })
})
