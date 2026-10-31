
export interface NVMeasurementRequest {
  magnetic_field_nt: [number, number, number]
  nv_axis: [number, number, number]
  frequencies_mhz: number[]
  contrast: number
  linewidth_mhz: number
  reference_photon_count: number
  seed: number
  zero_field_splitting_mhz?: number
}

export interface NVSimulation {
  frequencies_mhz: number[]
  ideal_fluorescence: number[]
  measured_fluorescence: number[]
  photon_counts: number[]
  reference_photon_count: number
  lower_mhz: number
  upper_mhz: number
  projected_field_nt: number
}

export interface NVFieldEstimation {
  lower_mhz: number
  upper_mhz: number
  projected_field_magnitude_nt: number
  residual_rmse: number
  fit_success: boolean
}

export interface NVFieldUncertainty {
  fisher_information_per_nt_squared: number
  crlb_std_nt: number | null
  identifiable_locally: boolean
}

export interface NVMeasurementResponse {
  simulation: NVSimulation
  estimation: NVFieldEstimation | null
  uncertainty: NVFieldUncertainty | null
  fit_success: boolean
}

interface APIError {
  detail?: unknown
}

function formatAPIError(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item: unknown) => {
        if (
          typeof item === 'object' &&
          item !== null &&
          'msg' in item &&
          typeof item.msg === 'string'
        ) {
          return item.msg
        }
        return 'Invalid measurement parameter'
      })
      .join('; ')
  }

  return 'The measurement request failed'
}

export async function runNVMeasurement(
  request: NVMeasurementRequest,
  signal?: AbortSignal,
): Promise<NVMeasurementResponse> {
  const response = await fetch('/api/v1/nv/odmr/measurement', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal,
  })

  if (!response.ok) {
    let message = `Measurement failed (HTTP ${response.status})`

    try {
      const error = (await response.json()) as APIError
      message = formatAPIError(error.detail)
    } catch {
      // Preserve the HTTP status when the response is not JSON.
    }

    throw new Error(message)
  }

  return (await response.json()) as NVMeasurementResponse
}

export function createFrequencyGrid(
  startMHz: number,
  endMHz: number,
  samples: number,
): number[] {
  if (
    !Number.isFinite(startMHz) ||
    !Number.isFinite(endMHz) ||
    !Number.isInteger(samples) ||
    samples < 5 ||
    samples > 5000 ||
    endMHz <= startMHz
  ) {
    throw new Error('Invalid frequency-grid parameters')
  }

  const step = (endMHz - startMHz) / (samples - 1)

  return Array.from(
    { length: samples },
    (_, index) => startMHz + index * step,
  )
}
