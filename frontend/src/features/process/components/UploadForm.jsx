import { useRef, useState } from 'react'

import { useMutation } from '@tanstack/react-query'

import { submitProcessRequest } from '../../../lib/api-client'

const validationGuidanceByCode = {
  missing_file: 'No photo detected. Tap Take Photo or choose an image to continue.',
  invalid_mime_type: 'Unsupported file type. Retake or upload a JPG, PNG, or WEBP image.',
  file_too_large: 'Image is too large. Retake with a lower resolution or upload a smaller file.',
  image_decode_failed: 'We could not read that image. Retake a clearer photo and try again.',
  image_too_large_pixels: 'Image dimensions are too large. Retake with lower resolution and retry.',
}

export default function UploadForm() {
  const [file, setFile] = useState(null)
  const cameraInputRef = useRef(null)

  const mutation = useMutation({
    mutationFn: () => submitProcessRequest(file),
  })

  const handleSubmit = (event) => {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <section>
      {/* Hidden file input with camera capture for "Take Photo" */}
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: 'none' }}
        aria-hidden="true"
        onChange={(event) => setFile(event.target.files?.[0] || null)}
      />

      <form onSubmit={handleSubmit} aria-label="process-upload-form">
        <button
          type="button"
          onClick={() => cameraInputRef.current?.click()}
        >
          Take Photo
        </button>
        <div style={{ marginTop: '0.75rem' }}>
          <label htmlFor="upload-image">Upload image</label>
          <input
            id="upload-image"
            name="upload-image"
            type="file"
            accept="image/*"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </div>
        <button type="submit" disabled={mutation.isPending} style={{ marginTop: '0.75rem' }}>
          {mutation.isPending ? 'Submitting...' : 'Submit'}
        </button>
      </form>

      <div style={{ marginTop: '1rem' }}>
        <h2>Processing Status</h2>
        {!mutation.data && !mutation.error && !mutation.isPending && <p>Waiting for submission.</p>}
        {mutation.isPending && <p>Uploading image...</p>}
        {mutation.error && (
          <p role="alert">
            {validationGuidanceByCode[mutation.error.code] || mutation.error.message}
          </p>
        )}
        {mutation.data && (
          <p>
            Valid image accepted — continuing to OCR processing... ({mutation.data.request_id})
          </p>
        )}
      </div>
    </section>
  )
}
