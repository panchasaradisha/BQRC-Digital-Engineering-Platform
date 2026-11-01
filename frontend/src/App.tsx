import { useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import {
  Activity,
  AlertCircle,
  Atom,
  BookOpen,
  BookMarked,
  Cable,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  CircuitBoard,
  Cpu,
  Database,
  Download,
  Eye,
  ExternalLink,
  FileJson,
  FlaskConical,
  Gauge,
  GitCompareArrows,
  GraduationCap,
  HardDrive,
  Info,
  Layers3,
  Lightbulb,
  LoaderCircle,
  Magnet,
  Network,
  Play,
  Plug,
  Radio,
  Rocket,
  RotateCcw,
  ScanLine,
  ShieldCheck,
  Server,
  Target,
  Usb,
  Waves,
  Workflow,
} from 'lucide-react'
import {
  Area,
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  createFrequencyGrid,
  runNVMeasurement,
  type NVMeasurementRequest,
  type NVMeasurementResponse,
} from './api/nv'
import './App.css'

type Vector3 = [number, number, number]
type WorkspaceTab = 'simulation' | 'hardware' | 'visualizations' | 'learn' | 'architecture'

interface FormState {
  magneticField: Vector3
  nvAxis: Vector3
  frequencyStart: number
  frequencyEnd: number
  samples: number
  contrast: number
  linewidth: number
  photonCount: number
  seed: number
}

type SourceClass = 'physics_model' | 'validated_model_output' | 'bqrc_default' | 'engineering_assumption' | 'user_override'

interface ParameterProvenance {
  parameter: keyof FormState
  label: string
  source_class: Exclude<SourceClass, 'user_override'>
  default_value: string
  source: string
  reference: string
  reference_url?: string
  validation: string
}

interface RequirementReference {
  id: string
  area: string
  status: 'Implemented' | 'Partial' | 'Concept' | 'Planned'
  source: string
  note: string
  requirements: string[]
  links: Array<{ label: string; url: string }>
  localReferences?: string[]
}

interface V1TraceabilityItem {
  id: string
  title: string
  status: 'Verified' | 'Implemented' | 'Partial' | 'Planned'
  verification: string
  evidence: string
  note: string
}

interface NVOrientation {
  id: 'NV1' | 'NV2' | 'NV3' | 'NV4'
  miller: string
  axis: Vector3
  colorClass: string
  color: string
}

interface NVOrientationMeasurement {
  orientation: NVOrientation
  response: NVMeasurementResponse
  seed: number
}

interface VectorReconstruction {
  candidate: Vector3
  opposite: Vector3
  magnitude: number
  residualRms: number
  signs: number[]
}

const DEFAULT_FORM: FormState = {
  magneticField: [22_549.946, -216.079, 8_304.235],
  nvAxis: [0, 0, 1],
  frequencyStart: 2_850,
  frequencyEnd: 2_890,
  samples: 401,
  contrast: 0.1,
  linewidth: 1,
  photonCount: 1_000_000,
  seed: 2_027,
}

const PRESETS: Array<{ label: string; field: Vector3; axis: Vector3 }> = [
  { label: 'IGRF-14 scenario t₀', field: [22_549.946, -216.079, 8_304.235], axis: [0, 0, 1] },
  { label: 'Controlled +50 µT', field: [50_000, 0, 0], axis: [1, 0, 0] },
  { label: 'Polarity check −35 µT', field: [-35_000, 0, 0], axis: [1, 0, 0] },
  { label: 'Oblique geometry', field: [42_000, 18_000, -9_000], axis: [1, 1, 1] },
]

const NV_ORIENTATIONS: NVOrientation[] = [
  { id: 'NV1', miller: '[111]', axis: [1 / Math.sqrt(3), 1 / Math.sqrt(3), 1 / Math.sqrt(3)], colorClass: 'nv-one', color: '#147ac0' },
  { id: 'NV2', miller: '[−111]', axis: [-1 / Math.sqrt(3), 1 / Math.sqrt(3), 1 / Math.sqrt(3)], colorClass: 'nv-two', color: '#725cca' },
  { id: 'NV3', miller: '[1−11]', axis: [1 / Math.sqrt(3), -1 / Math.sqrt(3), 1 / Math.sqrt(3)], colorClass: 'nv-three', color: '#10998d' },
  { id: 'NV4', miller: '[11−1]', axis: [1 / Math.sqrt(3), 1 / Math.sqrt(3), -1 / Math.sqrt(3)], colorClass: 'nv-four', color: '#d18a2f' },
]

const NV_VECTOR_REFERENCES = [
  {
    label: 'AIP widefield NV review',
    url: 'https://doi.org/10.1063/5.0066733',
    claim: 'Four ⟨111⟩ orientation families, up to eight ODMR resonances, and vector recovery from assigned transition pairs.',
  },
  {
    label: 'Polarization-assigned vector magnetometry',
    url: 'https://doi.org/10.1038/s41598-026-50385-6',
    claim: 'Orientation assignment, four projection constraints, least-squares reconstruction, and the remaining global ±B ambiguity.',
  },
]

const PARAMETER_PROVENANCE: ParameterProvenance[] = [
  {
    parameter: 'magneticField',
    label: 'Magnetic-field vector',
    source_class: 'validated_model_output',
    default_value: '[22,549.946, -216.079, 8,304.235] nT',
    source: 'Run Contract V1 scenario acquisition 0 · IGRF-14 body-frame output',
    reference: 'Rounded to 0.001 nT from configuration 29373e1e46e52995 at 2027-07-18T10:00:00Z; model output, not measured flight truth.',
    reference_url: 'https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field',
    validation: 'Scientific integration tested; software verified; not hardware validated',
  },
  {
    parameter: 'nvAxis',
    label: 'NV-axis vector',
    source_class: 'bqrc_default',
    default_value: '[0, 0, 1]',
    source: 'Run Contract V1 scenario sensor configuration',
    reference: 'Body-z NV axis from leo-iss-like-nv-v1; the backend normalizes the editable vector before projection.',
    reference_url: 'https://doi.org/10.1063/5.0066733',
    validation: 'Approved scenario geometry; not a measured crystal orientation',
  },
  {
    parameter: 'frequencyStart',
    label: 'Sweep start',
    source_class: 'bqrc_default',
    default_value: '2850 MHz',
    source: 'Run Contract V1 NV sensor configuration',
    reference: 'The 40 MHz scenario sweep spans the D ≈ 2.87 GHz physics anchor.',
    reference_url: 'https://doi.org/10.1063/5.0066733',
    validation: 'Scenario-validated model setting',
  },
  {
    parameter: 'frequencyEnd',
    label: 'Sweep end',
    source_class: 'bqrc_default',
    default_value: '2890 MHz',
    source: 'Run Contract V1 NV sensor configuration',
    reference: 'The 40 MHz scenario sweep spans the D ≈ 2.87 GHz physics anchor; temperature coupling remains a known limitation.',
    reference_url: 'https://doi.org/10.1063/5.0066733',
    validation: 'Scenario-validated model setting',
  },
  {
    parameter: 'samples',
    label: 'Frequency samples',
    source_class: 'bqrc_default',
    default_value: '401',
    source: 'Run Contract V1 NV sensor configuration',
    reference: 'Full scenario sweep density; the contract notes this setting is computationally expensive.',
    validation: 'Software-tested scenario configuration',
  },
  {
    parameter: 'linewidth',
    label: 'ODMR linewidth',
    source_class: 'bqrc_default',
    default_value: '1 MHz',
    source: 'Run Contract V1 sensor and estimator configuration',
    reference: 'Actual linewidth depends on material, strain, temperature, microwave power, and hardware.',
    reference_url: 'https://doi.org/10.1063/5.0066733',
    validation: 'Model default; requires instrument calibration',
  },
  {
    parameter: 'contrast',
    label: 'ODMR contrast',
    source_class: 'bqrc_default',
    default_value: '0.1',
    source: 'Run Contract V1 sensor and estimator configuration',
    reference: 'A dimensionless simulation setting, not a universal NV-center value.',
    reference_url: 'https://doi.org/10.1063/5.0066733',
    validation: 'Model default; requires instrument calibration',
  },
  {
    parameter: 'photonCount',
    label: 'Reference photon count',
    source_class: 'bqrc_default',
    default_value: '1,000,000 counts',
    source: 'Run Contract V1 NV sensor configuration',
    reference: 'Poisson photon-count model; the scenario count budget is editable and is acquisition metadata available to the estimator.',
    reference_url: 'https://tf.nist.gov/general/pdf/3216.pdf',
    validation: 'Software-tested noise model; not detector calibrated',
  },
  {
    parameter: 'seed',
    label: 'Random seed',
    source_class: 'bqrc_default',
    default_value: '2027',
    source: 'Run Contract V1 scenario master seed',
    reference: 'Per-sensor, per-tick seeds are deterministically derived from this master seed; it is not a physical parameter.',
    validation: 'Deterministic software control',
  },
]

const REQUIREMENT_REFERENCES: RequirementReference[] = [
  {
    id: 'FE-01',
    area: 'Main dashboard',
    status: 'Partial',
    source: 'BQRC Run Contract V1 + CCSDS mission-data standards',
    note: 'Current view reports NV experiment state and a reproducible run contract; broader spacecraft telemetry still awaits an API.',
    requirements: ['BQRC-UI-001', 'BQRC-APP-001', 'BQRC-V1-017'],
    links: [{ label: 'CCSDS Blue Books', url: 'https://ccsds.org/view/bluebooks/' }],
    localReferences: ['docs/design/RUN_CONTRACT_V1.md'],
  },
  {
    id: 'FE-02',
    area: 'Orbit, Earth & microgravity',
    status: 'Partial',
    source: 'IERS reference systems + NASA microgravity explanation',
    note: 'The applied scenario runner propagates a circular orbit and evaluates environment truth; the frontend remains explanatory until a run API is exposed.',
    requirements: ['BQRC-ORB-001–007', 'BQRC-MGR-001–006', 'BQRC-UI-010'],
    links: [
      { label: 'IERS Conventions', url: 'https://www.iers.org/iers/en/dataproducts/conventions/conventions' },
      { label: 'NASA microgravity', url: 'https://www.nasa.gov/centers-and-facilities/glenn/what-is-microgravity/' },
    ],
    localReferences: ['src/bqrc/simulation/orbit.py', 'src/bqrc/simulation/runner.py'],
  },
  {
    id: 'FE-03',
    area: 'Virtual labs & sensor twins',
    status: 'Implemented',
    source: 'Peer-reviewed NV/ODMR literature + BQRC API',
    note: 'The typed backend is evaluated for one configurable axis and all four calibrated ⟨111⟩ orientation families; the frontend exposes eight transitions, four projection fits, and an ambiguity-preserving vector reconstruction.',
    requirements: ['BQRC-NV-001–006', 'BQRC-ODMR-001–009', 'BQRC-V1-007–011'],
    links: [
      { label: 'NV microscopy review', url: 'https://doi.org/10.1063/5.0066733' },
      { label: 'Four-axis vector reconstruction', url: 'https://doi.org/10.1038/s41598-026-50385-6' },
      { label: 'NIST electron γ/2π', url: 'https://physics.nist.gov/cgi-bin/cuu/Value?gammaebar%7Csearch_for=gyromagnetic+ratio' },
    ],
  },
  {
    id: 'FE-04',
    area: 'Space environment',
    status: 'Partial',
    source: 'IAGA IGRF-14 via NOAA/NCEI',
    note: 'IGRF-14 is verified in the core, but orbit-time field vectors are not yet exposed to this page.',
    requirements: ['BQRC-ENV-001–005', 'BQRC-MAG-001–009', 'BQRC-V1-003–006'],
    links: [{ label: 'Official IGRF', url: 'https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field' }],
    localReferences: ['configs/scenarios/leo_iss_like_nv_v1.json'],
  },
  {
    id: 'FE-05',
    area: 'Analysis & uncertainty',
    status: 'Implemented',
    source: 'Cramér–Rao information bound',
    note: 'Residual, fit, Fisher information, and local CRLB views are active for the NV pipeline.',
    requirements: ['BQRC-UNC-001–006', 'BQRC-ANA-001–007', 'BQRC-V1-012–014'],
    links: [{ label: 'NIST CRLB reference', url: 'https://www.itl.nist.gov/div898/winds/pdf_files/A3-3_Lieblein.pdf' }],
  },
  {
    id: 'FE-06',
    area: 'Experiment & dataset factory',
    status: 'Partial',
    source: 'BQRC Run Contract V1 + W3C PROV data model',
    note: 'The backend writes config, manifest, L1 acquisitions, L4 measurements, and verification errors; browser export preserves defaults, sources, links, and overrides.',
    requirements: ['BQRC-CORE-017–022', 'BQRC-DATA-001–012', 'BQRC-V1-020'],
    links: [{ label: 'W3C PROV overview', url: 'https://www.w3.org/TR/prov-overview/' }],
    localReferences: ['src/bqrc/simulation/storage.py', 'docs/design/RUN_CONTRACT_V1.md'],
  },
  {
    id: 'FE-07',
    area: 'Mission control & telemetry',
    status: 'Planned',
    source: 'CCSDS telemetry and command exchange standards',
    note: 'No start/pause/command controls are shown until a real mission-control backend exists.',
    requirements: ['BQRC-API-002', 'BQRC-UI-002', 'BQRC-MSN-001–006', 'BQRC-TLM-001–007'],
    links: [{ label: 'CCSDS Blue Books', url: 'https://ccsds.org/view/bluebooks/' }],
  },
  {
    id: 'FE-08',
    area: 'Knowledge, design & evidence',
    status: 'Implemented',
    source: 'Run Contract V1 + W3C PROV + explicit model maturity labels',
    note: 'The evidence register separates sourced facts, validated model output, model defaults, engineering assumptions, and user overrides.',
    requirements: ['BQRC-KNW-001–011', 'BQRC-VER-001–009', 'BQRC-SCI-001–010'],
    links: [{ label: 'W3C provenance standard', url: 'https://www.w3.org/TR/prov-overview/' }],
    localReferences: ['ASSUMPTIONS.md section 44', 'tests/unit/test_architecture_rules.py'],
  },
  {
    id: 'FE-09',
    area: 'Application-wide UX',
    status: 'Partial',
    source: 'W3C WCAG 2.2',
    note: 'Responsive controls, labeled charts, keyboard-native inputs, status, errors, and reduced-motion support are in scope.',
    requirements: ['BQRC-UI-003–010', 'BQRC-SEC-001–005'],
    links: [{ label: 'WCAG 2.2', url: 'https://www.w3.org/TR/WCAG22/' }],
  },
]

const V1_REQUIREMENT_TRACEABILITY: V1TraceabilityItem[] = [
  { id: 'BQRC-V1-001', title: 'Master clock', status: 'Verified', verification: 'Test', evidence: 'tests/unit/test_simulation_clock.py', note: 'Integer-step deterministic clock and multi-rate scheduling.' },
  { id: 'BQRC-V1-002', title: 'Position input', status: 'Verified', verification: 'Scientific test', evidence: 'tests/scientific/test_two_body_orbit.py', note: 'Basic circular two-body orbital source.' },
  { id: 'BQRC-V1-003', title: 'Geomagnetic reference', status: 'Verified', verification: 'Scientific comparison', evidence: 'tests/scientific/test_igrf14_reference.py', note: 'IGRF-14 reference implementation and dataset.' },
  { id: 'BQRC-V1-004', title: 'Magnetic truth', status: 'Verified', verification: 'Test + inspection', evidence: 'tests/unit/test_architecture_rules.py', note: 'L0 truth isolated from sensors and algorithms.' },
  { id: 'BQRC-V1-005', title: 'Frame transformation', status: 'Verified', verification: 'Scientific test', evidence: 'tests/unit/test_attitude_aware_nv.py', note: 'NED-to-body attitude-aware magnetic projection.' },
  { id: 'BQRC-V1-006', title: 'Local disturbance', status: 'Planned', verification: 'Not tested', evidence: 'REQUIREMENTS.md', note: 'No validated local magnetic-disturbance model is connected yet.' },
  { id: 'BQRC-V1-007', title: 'NV physics', status: 'Verified', verification: 'Scientific test', evidence: 'tests/unit/test_nv_resonance.py', note: 'Evidence-based first-order NV resonance model.' },
  { id: 'BQRC-V1-008', title: 'ODMR generation', status: 'Verified', verification: 'Scientific test', evidence: 'tests/unit/test_odmr_spectrum.py', note: 'Two-resonance normalized fluorescence model.' },
  { id: 'BQRC-V1-009', title: 'Noise', status: 'Verified', verification: 'Test', evidence: 'tests/unit/test_odmr_shot_noise.py', note: 'Deterministic Poisson photon-count sampling.' },
  { id: 'BQRC-V1-010', title: 'ODMR estimation', status: 'Verified', verification: 'Test', evidence: 'tests/unit/test_odmr_field_estimator.py', note: 'Classical multi-start lineshape estimator.' },
  { id: 'BQRC-V1-011', title: 'Magnetic estimate', status: 'Verified', verification: 'Integration test', evidence: 'tests/unit/test_nv_measurement.py', note: 'Unsigned NV-axis field magnitude from splitting.' },
  { id: 'BQRC-V1-012', title: 'Truth comparison', status: 'Verified', verification: 'Scientific test', evidence: 'tests/scientific/test_run_nv_scenario.py', note: 'ErrorRecord compares L4 estimate with hidden L0 truth.' },
  { id: 'BQRC-V1-013', title: 'Quality', status: 'Verified', verification: 'Test', evidence: 'tests/scientific/test_run_nv_scenario.py', note: 'Fit state and UNCALIBRATED / DEGRADED flags.' },
  { id: 'BQRC-V1-014', title: 'Uncertainty', status: 'Verified', verification: 'Scientific test', evidence: 'tests/unit/test_nv_field_uncertainty.py', note: 'Local Poisson CRLB with explicit interpretation limits.' },
  { id: 'BQRC-V1-015', title: 'IMU channel', status: 'Planned', verification: 'Not tested', evidence: 'REQUIREMENTS.md', note: 'A conventional IMU measurement channel is not implemented.' },
  { id: 'BQRC-V1-016', title: 'Backend', status: 'Partial', verification: 'Integration test', evidence: 'tests/unit/test_api_nv_measurement.py', note: 'NV measurement API exists; scenario-run control API is not exposed.' },
  { id: 'BQRC-V1-017', title: 'Web visualization', status: 'Implemented', verification: 'Demonstration', evidence: 'frontend/src/App.tsx', note: 'Live backend ODMR, four-orientation vector, residual, photon, resonance, and CRLB views.' },
  { id: 'BQRC-V1-018', title: 'Manual parameters', status: 'Implemented', verification: 'Demonstration', evidence: 'frontend/src/App.tsx', note: 'Approved values are editable and visibly marked as overrides.' },
  { id: 'BQRC-V1-019', title: 'Source information', status: 'Implemented', verification: 'Inspection', evidence: 'frontend/src/App.tsx', note: 'Parameter classes, sources, limitations, and references are visible.' },
  { id: 'BQRC-V1-020', title: 'Experiment export', status: 'Implemented', verification: 'Demonstration', evidence: 'frontend/src/App.tsx', note: 'JSON export preserves configuration, provenance, references, and overrides.' },
]

const DEFAULT_PROFILE = {
  id: 'leo-iss-like-nv-v1-acquisition-0',
  name: 'LEO ISS-like NV V1 · acquisition 0',
  maturity: 'validated_model_output_software_verified_not_hardware_validated',
  configuration_id: '29373e1e46e52995',
  epoch: '2027-07-18T10:00:00Z',
  geodetic_position: {
    latitude_deg: 0,
    longitude_deg: -85.63810212363023,
    altitude_m: 392_863,
  },
  reference_output: {
    magnetic_field_body_nt: [22_549.945612166146, -216.07931373535132, 8_304.234573554802],
    total_intensity_nt: 24_031.376349141938,
    projected_nv_axis_field_nt: 8_304.234573554802,
  },
  physics_constants: {
    zero_field_splitting_mhz: 2870,
    electron_gyromagnetic_ratio_mhz_per_t: 28_024.95,
  },
  defaults: DEFAULT_FORM,
  parameter_provenance: PARAMETER_PROVENANCE,
}

const RUN_CONTRACT_PROFILE = {
  id: 'run-contract-v1',
  status: 'implemented_vertical_slice',
  verified_test_count: 495,
  scenario_reference: 'configs/scenarios/leo_iss_like_nv_v1.json',
  contract_reference: 'docs/design/RUN_CONTRACT_V1.md',
  stages: [
    { level: 'Config', type: 'ScenarioConfig', detail: 'Frozen configuration + SHA-256 configuration_id' },
    { level: 'L0', type: 'TruthState', detail: 'Hidden orbit, environment, attitude, and reference truth' },
    { level: 'Boundary', type: 'SensorStimulus', detail: 'Physical body-frame field only; no truth labels' },
    { level: 'L1', type: 'ODMRAcquisition', detail: 'Raw photon counts + acquisition metadata' },
    { level: 'L4', type: 'Measurement', detail: 'Unsigned estimate, quality, provenance, and uncertainty' },
    { level: 'Verify', type: 'ErrorRecord', detail: 'Truth comparison outside sensor and algorithm layers' },
  ],
  run_outputs: ['config.json', 'manifest.json', 'acquisitions.npz', 'measurements.jsonl', 'errors.jsonl'],
  limitations: ['kinematic attitude', 'quasi-static sweep', 'uncalibrated L4', 'CRLB assumes contrast, linewidth, and D are exact'],
}

function formatNumber(value: number, maximumFractionDigits = 2): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits,
  }).format(value)
}

function formatScientific(value: number): string {
  return value.toExponential(3)
}

function collectParameterOverrides(form: FormState) {
  const overrides: Array<{
    parameter: string
    default_value: number
    user_value: number
    source_class: 'user_override'
  }> = []

  const scalarKeys: Array<Exclude<keyof FormState, 'magneticField' | 'nvAxis'>> = [
    'frequencyStart',
    'frequencyEnd',
    'samples',
    'contrast',
    'linewidth',
    'photonCount',
    'seed',
  ]

  scalarKeys.forEach((key) => {
    if (form[key] !== DEFAULT_FORM[key]) {
      overrides.push({
        parameter: key,
        default_value: DEFAULT_FORM[key],
        user_value: form[key],
        source_class: 'user_override',
      })
    }
  })

  ;(['magneticField', 'nvAxis'] as const).forEach((key) => {
    form[key].forEach((value, index) => {
      if (value !== DEFAULT_FORM[key][index]) {
        overrides.push({
          parameter: `${key}.${['x', 'y', 'z'][index]}`,
          default_value: DEFAULT_FORM[key][index],
          user_value: value,
          source_class: 'user_override',
        })
      }
    })
  })

  return overrides
}

function validateForm(form: FormState): string | null {
  const numericValues = [
    ...form.magneticField,
    ...form.nvAxis,
    form.frequencyStart,
    form.frequencyEnd,
    form.samples,
    form.contrast,
    form.linewidth,
    form.photonCount,
    form.seed,
  ]

  if (numericValues.some((value) => !Number.isFinite(value))) {
    return 'All experiment parameters must be finite numbers.'
  }

  if (form.nvAxis.every((value) => value === 0)) {
    return 'NV axis must contain at least one non-zero component.'
  }

  if (form.frequencyEnd <= form.frequencyStart) {
    return 'Sweep end must be greater than sweep start.'
  }

  if (!(form.frequencyStart < 2_870 && form.frequencyEnd > 2_870)) {
    return 'The microwave sweep must span the 2,870 MHz zero-field splitting.'
  }

  if (!Number.isInteger(form.samples) || form.samples < 5 || form.samples > 5_000) {
    return 'Samples must be an integer from 5 to 5,000.'
  }

  if (form.contrast <= 0 || form.contrast > 0.5) {
    return 'Contrast must be greater than 0 and no more than 0.5.'
  }

  if (form.linewidth <= 0) {
    return 'Linewidth must be greater than 0 MHz.'
  }

  if (form.photonCount <= 0 || form.photonCount > 1e12) {
    return 'Reference photon count must be greater than 0 and no more than 10¹².'
  }

  if (!Number.isInteger(form.seed) || form.seed < 0 || form.seed > 2 ** 32 - 1) {
    return 'Seed must be an integer from 0 to 4,294,967,295.'
  }

  return null
}

function dotVector(left: Vector3, right: Vector3): number {
  return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]
}

function vectorMagnitude(vector: Vector3): number {
  return Math.sqrt(dotVector(vector, vector))
}

function reconstructVectorFromUnsignedProjections(
  measurements: NVOrientationMeasurement[],
): VectorReconstruction | null {
  if (measurements.length !== NV_ORIENTATIONS.length) return null

  const magnitudes = measurements.map(
    ({ response }) => response.estimation?.projected_field_magnitude_nt ?? null,
  )
  if (magnitudes.some((value) => value === null)) return null

  let best: VectorReconstruction | null = null

  for (let mask = 0; mask < 8; mask += 1) {
    const signs = [
      1,
      (mask & 1) === 0 ? 1 : -1,
      (mask & 2) === 0 ? 1 : -1,
      (mask & 4) === 0 ? 1 : -1,
    ]
    const signedProjections = magnitudes.map((value, index) => (value ?? 0) * signs[index])
    const candidate = NV_ORIENTATIONS.reduce<Vector3>(
      (vector, orientation, index) => [
        vector[0] + 0.75 * signedProjections[index] * orientation.axis[0],
        vector[1] + 0.75 * signedProjections[index] * orientation.axis[1],
        vector[2] + 0.75 * signedProjections[index] * orientation.axis[2],
      ],
      [0, 0, 0],
    )
    const residualRms = Math.sqrt(
      NV_ORIENTATIONS.reduce((sum, orientation, index) => {
        const residual = dotVector(candidate, orientation.axis) - signedProjections[index]
        return sum + residual ** 2
      }, 0) / NV_ORIENTATIONS.length,
    )
    const reconstruction: VectorReconstruction = {
      candidate,
      opposite: candidate.map((value) => -value) as Vector3,
      magnitude: vectorMagnitude(candidate),
      residualRms,
      signs,
    }

    if (best === null || reconstruction.residualRms < best.residualRms) best = reconstruction
  }

  return best
}

function formatVector(vector: Vector3, digits = 0): string {
  return `[${vector.map((value) => formatNumber(value, digits)).join(', ')}]`
}

function InputField({
  label,
  value,
  onChange,
  step,
  min,
  max,
  unit,
  sourceTag,
  overridden = false,
}: {
  label: string
  value: number
  onChange: (value: number) => void
  step?: number
  min?: number
  max?: number
  unit?: string
  sourceTag?: string
  overridden?: boolean
}) {
  return (
    <label className={`input-field ${overridden ? 'is-overridden' : ''}`}>
      <span className="field-label">
        <span>{label}</span>
        <span className="field-badges">
          {sourceTag && <small className="source-tag">{sourceTag}</small>}
          {overridden && <small>Override</small>}
        </span>
      </span>
      <span className="input-shell">
        <input
          type="number"
          value={value}
          step={step}
          min={min}
          max={max}
          onChange={(event) => onChange(event.currentTarget.valueAsNumber)}
        />
        {unit && <span className="input-unit">{unit}</span>}
      </span>
    </label>
  )
}

function VectorEditor({
  label,
  values,
  unit,
  defaults,
  sourceTag,
  onChange,
}: {
  label: string
  values: Vector3
  unit?: string
  defaults: Vector3
  sourceTag?: string
  onChange: (values: Vector3) => void
}) {
  const labels = ['X', 'Y', 'Z']

  return (
    <fieldset className={`vector-editor ${values.some((value, index) => value !== defaults[index]) ? 'has-overrides' : ''}`}>
      <legend>
        <span>{label}</span>
        <span className="field-badges">
          {sourceTag && <small className="source-tag">{sourceTag}</small>}
          {values.some((value, index) => value !== defaults[index]) && <small>Override</small>}
        </span>
      </legend>
      <div className="vector-grid">
        {values.map((value, index) => (
          <label className={value !== defaults[index] ? 'is-overridden' : ''} key={labels[index]}>
            <span>{labels[index]}</span>
            <span className="input-shell compact">
              <input
                aria-label={`${label} ${labels[index]}`}
                type="number"
                value={value}
                step={unit ? 1000 : 0.1}
                onChange={(event) => {
                  const next = [...values] as Vector3
                  next[index] = event.currentTarget.valueAsNumber
                  onChange(next)
                }}
              />
              {unit && <span className="input-unit">{unit}</span>}
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  )
}

function MetricCard({
  icon,
  eyebrow,
  value,
  unit,
  note,
  tone = 'blue',
}: {
  icon: ReactNode
  eyebrow: string
  value: string
  unit?: string
  note: string
  tone?: 'blue' | 'violet' | 'cyan' | 'green'
}) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <p className="metric-eyebrow">{eyebrow}</p>
        <p className="metric-value">
          {value} {unit && <span>{unit}</span>}
        </p>
        <p className="metric-note">{note}</p>
      </div>
    </article>
  )
}

const LEARNING_TOPICS = [
  {
    title: 'What BQRC is—and is not',
    level: 'Orientation',
    summary: 'A traceable digital-engineering platform for studying how quantum magnetic sensing can support resilient navigation research.',
    bigIdea: 'BQRC joins a physics model, an NV-center measurement model, an estimator and an evidence record. Its purpose is to make every input, transformation, output and limitation inspectable. The present vertical slice is research software: it is not flight-qualified, not a complete inertial-navigation system and not evidence that hardware has been tested.',
    method: ['Define a scenario and freeze its configuration.', 'Generate hidden orbit, attitude and environment truth.', 'Pass only a physical magnetic-field stimulus into the sensor model.', 'Create photon-count observations, estimate the field and qualify uncertainty.', 'Compare the estimate with hidden truth only inside verification.'],
    equations: [{ expression: 'scenario → truth → stimulus → acquisition → estimate → verification', meaning: 'The scientific chain; later stages may not secretly read the answer from an earlier truth product.' }],
    interpretation: 'A successful run proves that the declared software workflow executed and produced traceable artifacts. It does not prove real-world sensor performance.',
    projectUse: 'This mental model explains every workspace: Simulation performs the experiment, Hardware defines a future instrument boundary, Visualizations teach relationships, and Flow Architecture exposes ownership of data.',
    limits: ['No real instrument is connected.', 'Navigation fusion and flight qualification are outside the current slice.', 'Model agreement is not hardware validation.'],
    references: [{ label: 'Project requirements', url: '#project-documents' }, { label: 'System architecture', url: '#project-documents' }],
  },
  {
    title: 'Frames, vectors, units and signs',
    level: 'Mathematical foundation',
    summary: 'A magnetic vector is meaningful only together with its coordinate frame, units, time and sign convention.',
    bigIdea: 'BQRC distinguishes Earth-fixed, inertial, orbital, body and NV-axis descriptions. The same physical field has different numerical components after a rotation. A scalar magnitude is rotation-invariant, but a component such as B·n depends on the chosen NV direction n.',
    method: ['Name the source frame of every vector.', 'Transform with an explicit, normalized attitude rotation.', 'Record units at the API boundary.', 'Project the body-frame field onto each calibrated NV unit axis.', 'Keep signed reference values separate from unsigned spectral estimates.'],
    equations: [{ expression: 'B_body = R_body←source B_source', meaning: 'Rotate the source-frame magnetic vector into the sensor body frame.' }, { expression: 'B∥,i = nᵢ · B_body', meaning: 'Signed field projection along NV orientation i.' }, { expression: '|B| = √(Bx² + By² + Bz²)', meaning: 'Vector magnitude; this alone cannot specify direction.' }],
    interpretation: 'A sign change can represent a reversed axis definition rather than a changed field. Frame metadata and calibration matrices are therefore part of the measurement, not optional labels.',
    projectUse: 'The simulation form defines position and attitude inputs; orientation cards show per-axis projections; the architecture keeps the signed truth vector outside the estimator.',
    limits: ['A wrong orientation matrix can look like a plausible field.', 'Magnitude agreement cannot validate component signs.', 'Axes must be calibrated on the physical instrument.'],
    references: [{ label: 'Run Contract V1', url: '#project-documents' }],
  },
  {
    title: 'Orbit, gravity and microgravity',
    level: 'Space environment',
    summary: 'Microgravity is the small apparent-weight environment produced mainly by common free fall—not an absence of Earth’s gravity.',
    bigIdea: 'Gravity at low-Earth-orbit altitude remains substantial. The spacecraft, sensor and nearby free objects continuously fall around Earth together, so little support force is felt. Real platforms still experience residual acceleration from atmospheric drag, gravity gradients, attitude control, crew motion, pumps, fans, rotating equipment and structural vibration.',
    method: ['Use position and velocity to define the ideal orbit.', 'Propagate the vehicle and time deterministically.', 'Treat ideal common free fall as the baseline.', 'Add measured or validated disturbance terms only when their source and time base are known.', 'Label simulated acceleration separately from accelerometer telemetry.'],
    equations: [{ expression: 'a = −μ r / |r|³', meaning: 'Ideal two-body gravitational acceleration directed toward Earth.' }, { expression: 'v_circular = √(μ / r)', meaning: 'Circular-orbit speed for radius r in the ideal model.' }],
    interpretation: 'Floating does not mean g = 0. It means the local objects have nearly the same gravitational acceleration, leaving only small relative or non-gravitational accelerations.',
    projectUse: 'The current scenario provides deterministic two-body orbit context for time and position. It does not yet inject measured micro-vibration into the NV acquisition.',
    limits: ['No drag, flexible-body or control-system disturbance telemetry is connected.', 'The present visualization is conceptual, not an onboard accelerometer trace.', 'Microgravity affects experimental stability, but it is not itself the magnetic measurand.'],
    references: [{ label: 'NASA: What is microgravity?', url: 'https://www.nasa.gov/centers-and-facilities/glenn/what-is-microgravity/' }],
  },
  {
    title: 'Earth’s magnetic field and IGRF-14',
    level: 'Magnetic environment',
    summary: 'IGRF supplies a dated, position-dependent reference model of Earth’s large-scale main magnetic field.',
    bigIdea: 'The International Geomagnetic Reference Field represents the main field generated largely inside Earth using spherical-harmonic coefficients updated by the geomagnetic community. It is a model, not a local sensor observation. Spacecraft currents, magnetic materials, electronics, nearby payloads and short-scale external variations can make the field at the diamond different from the IGRF value.',
    method: ['Convert scenario time and position into the coordinates required by the model.', 'Evaluate the declared IGRF release and coefficient epoch.', 'Transform the model vector into the spacecraft or sensor frame.', 'Record model name, version, coefficients and transformation provenance.', 'Treat platform field and disturbance compensation as separate calibrated additions.'],
    equations: [{ expression: 'B_reference = IGRF(position, decimal year, model release)', meaning: 'Reference-field query with explicit place, time and version.' }, { expression: 'B_sensor = R B_reference + B_platform + δB', meaning: 'A future measurement model must account for platform field and residual disturbances.' }],
    interpretation: 'IGRF is an environmental prior or reference truth in simulation. A real magnetometer measures the total local field at its location.',
    projectUse: 'BQRC uses IGRF as a traceable environment source, records its release, and keeps reference truth separate from NV observations.',
    limits: ['It does not automatically include spacecraft magnetic contamination.', 'Model uncertainty and external-field variations remain separate concerns.', 'A model vector must not be presented as measured hardware data.'],
    references: [{ label: 'NOAA/NCEI IGRF-14', url: 'https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field' }],
  },
  {
    title: 'The NV⁻ center as a quantum sensor',
    level: 'Quantum physics',
    summary: 'A negatively charged nitrogen-vacancy defect in diamond provides a spin-1 ground state that can be prepared and read optically.',
    bigIdea: 'The defect consists of a substitutional nitrogen next to a missing carbon site. Its ground-state spin sublevels are labeled mₛ = 0 and mₛ = ±1. At approximately room temperature and zero magnetic field, the ±1 states lie about 2.87 GHz above mₛ = 0. Magnetic field, temperature, strain and electric field can shift the transition frequencies, so magnetometry requires a stated physical model and calibration.',
    method: ['Illuminate the diamond to polarize population preferentially toward mₛ = 0.', 'Apply microwave excitation near the spin-transition frequency.', 'Collect spin-dependent fluorescence.', 'Relate fitted resonance frequencies to a declared Hamiltonian or first-order approximation.', 'Calibrate orientation, frequency reference, contrast and environmental cross-sensitivities.'],
    equations: [{ expression: 'H/h ≈ D Sᶻ² + γₑ B·S', meaning: 'Simplified spin Hamiltonian: zero-field splitting plus electronic Zeeman interaction.' }, { expression: 'D ≈ 2.87 GHz', meaning: 'Room-temperature zero-field splitting used as the nominal spectral center—not a universal constant independent of conditions.' }],
    interpretation: 'The NV is quantum because discrete spin states and their coherent transitions encode the field. The dashboard measures an ensemble-style fluorescence spectrum, not a direct picture of a single electron.',
    projectUse: 'The sensor model turns a body-frame magnetic stimulus into resonance locations and a simulated photon-count spectrum.',
    limits: ['The first-order axial approximation weakens for strong off-axis fields or unresolved perturbations.', 'Temperature and strain can mimic magnetic frequency shifts.', 'The current model does not simulate the full optical cycle or density-matrix dynamics.'],
    references: [{ label: 'AIP widefield NV review', url: 'https://doi.org/10.1063/5.0066733' }],
  },
  {
    title: 'Optical pumping and fluorescence readout',
    level: 'Sensor operation',
    summary: 'Green excitation prepares the spin and red fluorescence provides an indirect, statistical readout of its state.',
    bigIdea: 'Optical excitation and spin-dependent non-radiative pathways make the mₛ = 0 state appear brighter than mₛ = ±1 under typical continuous-wave conditions. The detector sees photons or an analog photocurrent—not the magnetic field itself. Optical power, collection efficiency, background, detector gain, saturation and timing all affect the observed contrast.',
    method: ['Deliver stable excitation within the approved safety envelope.', 'Reject pump light and collect the fluorescence band.', 'Convert detector output to timestamped photon counts or calibrated intensity.', 'Measure background, saturation and dead-time behavior.', 'Store raw samples and acquisition settings before fitting.'],
    equations: [{ expression: 'N ∼ Poisson(λ)', meaning: 'A baseline photon-count model in which variance is approximately equal to the expected count λ.' }, { expression: 'contrast = (Ioff − Ion) / Ioff', meaning: 'One common ODMR contrast convention; the exact convention must be declared.' }],
    interpretation: 'Higher counts generally reduce shot-noise limits, but more laser power can also heat or saturate the system. Signal-to-noise must be evaluated with the actual instrument.',
    projectUse: 'BQRC generates Poisson counts around a modeled fluorescence spectrum and preserves them as L1 acquisition data.',
    limits: ['Poisson noise is a baseline, not a complete detector model.', 'No current hardware dead time, laser drift or camera fixed-pattern noise is modeled.', 'Fluorescence intensity alone is not a calibrated magnetic-field value.'],
    references: [{ label: 'AIP widefield NV review', url: 'https://doi.org/10.1063/5.0066733' }],
  },
  {
    title: 'ODMR, two transitions and eight resonances',
    level: 'Spectroscopy',
    summary: 'A microwave sweep produces two spin-transition resonances per NV orientation; four orientations can therefore contribute up to eight spectral resonances.',
    bigIdea: 'For one NV axis in the first-order axial model, the mₛ = 0 ↔ +1 and mₛ = 0 ↔ −1 transition frequencies move to opposite sides of D. Their separation measures the magnitude of the axial projection. These are two energy transitions or two spectral dips—not two physical depths in the diamond. With four crystallographic orientation families, the aggregate spectrum can contain eight contributions, although lines may overlap.',
    method: ['Sweep microwave frequency across the declared band.', 'Collect synchronized photon counts at every frequency.', 'Identify or jointly fit resonance lines.', 'Pair and assign lines to the correct NV orientation.', 'Convert each pair’s separation into an axial-projection magnitude.'],
    equations: [{ expression: 'fᵢ,± ≈ D ± γₑ (nᵢ·B)', meaning: 'First-order transition frequencies for orientation i.' }, { expression: '|B∥,i| ≈ |fᵢ,+ − fᵢ,−| / (2γₑ)', meaning: 'Unsigned axial projection inferred from the pair separation.' }],
    interpretation: 'A pair contains spectral information about one orientation. Eight resolved contributions are not guaranteed: symmetry, linewidth and weak bias fields can merge lines.',
    projectUse: 'Simulation shows the single-axis spectrum and the four-channel aggregate, fluorescence spectrum and photon-count trace with all eight transition contributions labeled by orientation.',
    limits: ['Peak assignment must be justified rather than inferred from color.', 'Overlapping resonances can make a fit non-identifiable.', 'The present simplified line shape and known-parameter assumptions are declared model choices.'],
    references: [{ label: 'AIP NV/ODMR review', url: 'https://doi.org/10.1063/5.0066733' }, { label: 'Four-axis vector study', url: 'https://doi.org/10.1038/s41598-026-50385-6' }],
  },
  {
    title: 'Four NV orientations and 3D reconstruction',
    level: 'Vector magnetometry',
    summary: 'Four tetrahedral ⟨111⟩ orientation families supply redundant axial constraints for reconstructing a three-component field.',
    bigIdea: 'Each assigned NV family measures the field projected on its own unit axis. Combining at least three independent signed projections can recover a 3D vector; the fourth adds redundancy and a consistency check. When the spectrum yields only projection magnitudes, sign branches must be tested and a global B ↔ −B ambiguity remains unless additional information resolves it.',
    method: ['Calibrate the four NV axes in the sensor frame.', 'Fit both transitions for every orientation.', 'Assign each resonance pair to the correct family.', 'Enumerate compatible projection signs and solve the overdetermined linear system.', 'Rank candidates by residual and conditioning; report unresolved symmetries.'],
    equations: [{ expression: 'p = N B', meaning: 'Projection system with four rows of calibrated NV unit axes.' }, { expression: 'B̂ = arg minB ‖N B − p‖²', meaning: 'Least-squares vector candidate from the assigned projections.' }, { expression: 'splittings ⇒ {B̂, −B̂}', meaning: 'Unsigned splittings retain a global two-fold ambiguity.' }],
    interpretation: 'The combined solution is meaningful only if the four individual channels agree with one physically consistent vector and the axis assignment is known.',
    projectUse: 'BQRC displays every orientation separately, the sign candidates, residual, condition information and the combined ± vector rather than hiding the ambiguity.',
    limits: ['A bias field, polarization assignment, prior or auxiliary sensor may be needed for absolute direction.', 'Poor geometry or merged lines increases uncertainty.', 'Independent-looking channels can share calibration errors.'],
    references: [{ label: 'Optically assigned vector magnetometry', url: 'https://doi.org/10.1038/s41598-026-50385-6' }, { label: 'AIP NV review', url: 'https://doi.org/10.1063/5.0066733' }],
  },
  {
    title: 'Spectral fitting and data quality',
    level: 'Estimation',
    summary: 'The estimator turns raw photon counts into resonance parameters only after checking identifiability and fit quality.',
    bigIdea: 'A fitted line center is an estimate under a chosen line shape, noise model and parameter set. Baseline, contrast, linewidth, overlap and sampling density can trade off against one another. An optimizer returning a number does not by itself make that number scientifically valid.',
    method: ['Validate finite, monotonic frequency samples and non-negative counts.', 'Choose a declared line-shape and baseline model.', 'Fit with physical parameter bounds and deterministic initialization.', 'Inspect convergence, residual structure and peak separation.', 'Emit quality flags when the model is weak, ambiguous or out of range.'],
    equations: [{ expression: 'μ(f; θ) = baseline × [1 − Σ contrastⱼ L(f; fⱼ, Γⱼ)]', meaning: 'Illustrative multi-resonance fluorescence model.' }, { expression: 'residualᵢ = countᵢ − μ(fᵢ; θ̂)', meaning: 'Difference used to inspect model agreement; structure in residuals can reveal missing physics.' }],
    interpretation: 'Small residuals support consistency with the fitted model, not proof that the model is physically complete. Quality state, parameter bounds and residual plots must be read together.',
    projectUse: 'The result cards expose fit status, RMSE, transition locations and per-orientation quality. Raw traces remain available beside the estimate.',
    limits: ['Current simulation does not reproduce every laboratory artifact.', 'Fit quality is not calibration accuracy.', 'A visually smooth curve can still be biased.'],
    references: [{ label: 'AIP NV measurement review', url: 'https://doi.org/10.1063/5.0066733' }],
  },
  {
    title: 'Uncertainty, CRLB, error and validation',
    level: 'Metrology',
    summary: 'CRLB, reported uncertainty and realized truth error answer different questions and must never be used as synonyms.',
    bigIdea: 'The Cramér–Rao lower bound is a local theoretical variance bound for an estimator under specific regularity assumptions, likelihood and known-parameter choices. A realized error is the estimate minus a known reference in one simulated trial. A measurement uncertainty statement should include all relevant statistical and systematic components and explain its coverage interpretation.',
    method: ['Declare the measurand and the likelihood model.', 'Compute Fisher information only for the parameters assumed estimable.', 'State which nuisance parameters are fixed or omitted.', 'Report CRLB as a model-based precision floor.', 'Use repeatability, calibration and truth comparison to validate broader performance.'],
    equations: [{ expression: 'Var(θ̂) ≥ 1 / I(θ)', meaning: 'Scalar Cramér–Rao inequality for an unbiased estimator under its assumptions.' }, { expression: 'error = estimate − reference', meaning: 'Signed realized difference available only when a defensible reference exists.' }, { expression: 'u_total² = u_stat² + u_cal² + u_model² + …', meaning: 'Illustrative uncertainty-budget structure; covariance terms may also be required.' }],
    interpretation: 'A CRLB smaller than the observed error is not automatically a contradiction. Bias, model mismatch, unmodeled nuisance parameters or a particular random draw may explain the difference.',
    projectUse: 'BQRC labels CRLB as an optimistic local bound, keeps signed truth error in verification, and avoids presenting either as a universal confidence interval.',
    limits: ['The current CRLB is conditional on the implemented photon and line-shape model.', 'Systematic calibration uncertainty is not fully represented.', 'Hardware validation needs repeated, traceable reference experiments.'],
    references: [{ label: 'NIST measurement uncertainty', url: 'https://www.nist.gov/pml/nist-technical-note-1297' }],
  },
  {
    title: 'Truth, acquisition, estimate and provenance',
    level: 'Scientific integrity',
    summary: 'BQRC treats the correct answer, raw observations, algorithm outputs and verification comparisons as different governed products.',
    bigIdea: 'A simulator knows hidden truth, but a real sensor never does. Allowing an estimator to access truth creates leakage and unrealistically good results. Provenance records which entities, activities and responsible agents produced an artifact so another researcher can understand and reproduce the run.',
    method: ['Create immutable configuration and identity hashes.', 'Generate L0 truth behind a verification boundary.', 'Expose only SensorStimulus to the sensor model or adapter.', 'Store L1 acquisition before estimation.', 'Store L4 measurement and separate ErrorRecord after comparison.'],
    equations: [{ expression: 'hash(config) + versions + sources + timestamps → run identity', meaning: 'Minimum evidence needed to associate outputs with the exact declared run.' }],
    interpretation: 'Traceability does not guarantee that a model is correct; it makes the model, inputs and limitations inspectable enough to challenge and reproduce.',
    projectUse: 'The architecture tab shows the boundary; exports contain the frozen config, manifest, acquisitions, measurements and verification errors as separate artifacts.',
    limits: ['A missing source or calibration breaks the evidence chain.', 'Truth is available only in simulation or controlled reference tests.', 'Provenance should record limitations, not merely file names.'],
    references: [{ label: 'W3C PROV overview', url: 'https://www.w3.org/TR/prov-overview/' }, { label: 'Run Contract V1', url: '#project-documents' }],
  },
  {
    title: 'Operating BQRC and moving to hardware',
    level: 'Practitioner workflow',
    summary: 'Use the simulation as a traceable learning and verification tool, then integrate hardware only through a calibrated observable-data adapter.',
    bigIdea: 'The safest path is incremental: understand a traced default, vary one factor at a time, inspect channel-level evidence, export the complete run, then substitute real L1 acquisition only after the instrument identity, protocol, calibration, timing and safety controls are known.',
    method: ['Read the learning path and architecture boundary.', 'Run the traced default without overrides.', 'Inspect spectrum, photon trace, four orientations, combined vector, quality and CRLB.', 'Change one parameter and explain the expected effect before rerunning.', 'Export and compare run identities.', 'For hardware, implement and validate an adapter that emits frequency, counts, timestamps, provenance and quality flags.'],
    equations: [{ expression: 'same contract, different acquisition source', meaning: 'Simulation and hardware should meet the same validated L1 boundary without pretending they have the same provenance.' }],
    interpretation: 'A real connection is complete only when the UI, backend adapter, instrument protocol, time base, calibration evidence and safety envelope all agree.',
    projectUse: 'Hardware currently validates a local profile shape but intentionally disables connection. The next implementation step requires the actual manufacturer, model, transport and command/data specification.',
    limits: ['The UI must not control laser or microwave hazards without engineered interlocks.', 'File replay must be labeled as replay, not live acquisition.', 'Do not compare hardware estimates with simulated truth as if they share a common reference.'],
    references: [{ label: 'Hardware workspace', url: '#top' }, { label: 'System architecture', url: '#project-documents' }],
  },
]

function HardwareWorkspace() {
  const [transport, setTransport] = useState('USB / serial')
  const [resource, setResource] = useState('')
  const [profileChecked, setProfileChecked] = useState(false)

  return (
    <section className="workspace-page" role="tabpanel" id="workspace-panel" aria-labelledby="workspace-tab-hardware">
      <div className="workspace-page-hero hardware-hero">
        <div><p className="section-kicker">Hardware integration</p><h1>Connect the optical, microwave and acquisition chain</h1><p>Prepare one traceable device profile for a real NV magnetometer. No device is currently connected, and the platform does not invent hardware telemetry.</p></div>
        <div className="workspace-state planned"><Cable size={17} /><span><strong>Adapter required</strong>Connection UI ready · driver and API pending</span></div>
      </div>

      <div className="hardware-signal-chain" aria-label="NV hardware signal chain">
        {[
          { icon: <Lightbulb size={20} />, title: '532 nm laser', note: 'Spin preparation & fluorescence excitation' },
          { icon: <Atom size={20} />, title: 'Diamond NV head', note: 'Four ⟨111⟩ orientation families' },
          { icon: <Radio size={20} />, title: 'Microwave source', note: 'Frequency sweep near 2.87 GHz' },
          { icon: <Eye size={20} />, title: 'Photodetector', note: 'Photon counts or analog fluorescence' },
          { icon: <CircuitBoard size={20} />, title: 'DAQ & timing', note: 'Synchronized frequency/count samples' },
          { icon: <Server size={20} />, title: 'BQRC adapter', note: 'Validation, provenance and L1 acquisition' },
        ].map((item, index) => <div className="hardware-node" key={item.title}><span>{item.icon}</span><small>0{index + 1}</small><strong>{item.title}</strong><p>{item.note}</p></div>)}
      </div>

      <div className="hardware-layout">
        <article className="integration-card">
          <div className="page-card-heading"><Usb size={18} /><div><h2>Connection profile</h2><p>Local configuration only—nothing is transmitted.</p></div></div>
          <div className="connection-form">
            <label><span>Transport</span><select value={transport} onChange={(event) => setTransport(event.currentTarget.value)}><option>USB / serial</option><option>Ethernet / TCP</option><option>Vendor SDK</option><option>File replay</option></select></label>
            <label><span>Device resource</span><input value={resource} onChange={(event) => { setResource(event.currentTarget.value); setProfileChecked(false) }} placeholder="Example: COM4 or 192.168.1.50" /></label>
            <label><span>Acquisition contract</span><input value="frequency_mhz + photon_counts + timestamps" readOnly /></label>
            <label><span>Calibration state</span><input value="Required before scientific measurement" readOnly /></label>
          </div>
          <div className="connection-actions"><button type="button" onClick={() => setProfileChecked(true)}><ShieldCheck size={14} /> Validate profile shape</button><button type="button" disabled><Plug size={14} /> Connect hardware</button></div>
          {profileChecked && <div className="profile-result" role="status"><CheckCircle2 size={15} /><p><strong>Profile structure is ready.</strong> {resource ? `${transport} resource “${resource}” is recorded locally.` : 'Add a device resource before driver integration.'} A vendor/model-specific adapter and authenticated backend connection are still required.</p></div>}
        </article>

        <article className="integration-card">
          <div className="page-card-heading"><Cpu size={18} /><div><h2>Information needed for a real driver</h2><p>Provide these before connection code can be scientifically validated.</p></div></div>
          <ul className="readiness-list">
            <li><span>01</span><div><strong>Instrument identity</strong><p>Manufacturer, model, firmware and serial/asset identifier.</p></div></li>
            <li><span>02</span><div><strong>Transport specification</strong><p>USB VID/PID, serial framing, IP protocol or supported SDK.</p></div></li>
            <li><span>03</span><div><strong>Command & data schema</strong><p>Sweep commands, count format, timestamps, units and error codes.</p></div></li>
            <li><span>04</span><div><strong>Timing & synchronization</strong><p>Clock source, trigger wiring, latency and dropped-sample behavior.</p></div></li>
            <li><span>05</span><div><strong>Calibration evidence</strong><p>Frequency reference, detector gain, orientation matrix and uncertainty.</p></div></li>
            <li><span>06</span><div><strong>Safety envelope</strong><p>Laser, microwave, thermal and power interlocks controlled outside this UI.</p></div></li>
          </ul>
        </article>
      </div>

      <article className="hardware-contract-card">
        <div className="page-card-heading"><FileJson size={18} /><div><h2>Proposed hardware-to-BQRC boundary</h2><p>The adapter must emit observables and provenance—not hidden truth.</p></div></div>
        <div className="contract-table-wrap"><table><thead><tr><th>Field</th><th>Purpose</th><th>Required behavior</th></tr></thead><tbody>
          <tr><td><code>frequency_mhz[]</code></td><td>Microwave sample coordinates</td><td>Monotonic, finite and unit-declared</td></tr>
          <tr><td><code>photon_counts[]</code></td><td>Raw detector observations</td><td>Non-negative integers; same length as frequency</td></tr>
          <tr><td><code>timestamp_utc</code></td><td>Acquisition timing</td><td>Traceable clock source and uncertainty</td></tr>
          <tr><td><code>device_provenance</code></td><td>Instrument identity</td><td>Model, serial, firmware, driver and configuration hash</td></tr>
          <tr><td><code>quality_flags[]</code></td><td>Acquisition validity</td><td>Explicit saturation, dropout, interlock and calibration flags</td></tr>
        </tbody></table></div>
      </article>
    </section>
  )
}

function VisualizationWorkspace({ response, orientationMeasurements, vectorReconstruction }: { response: NVMeasurementResponse | null; orientationMeasurements: NVOrientationMeasurement[]; vectorReconstruction: VectorReconstruction | null }) {
  return (
    <section className="workspace-page" role="tabpanel" id="workspace-panel" aria-labelledby="workspace-tab-visualizations">
      <div className="workspace-page-hero visualization-hero"><div><p className="section-kicker">Visualization atlas</p><h1>See how environment, quantum sensing and evidence connect</h1><p>A guided visual overview. Numerical values appear only when they come from the live simulation or an explicitly labeled reference model.</p></div><div className={`workspace-state ${response ? 'ready' : 'planned'}`}><Activity size={17} /><span><strong>{response ? 'Live result available' : 'No active result'}</strong>{response ? 'Simulation values linked below' : 'Run Simulation to populate metrics'}</span></div></div>

      <div className="visualization-atlas-grid">
        <article className="atlas-card orbit-atlas"><div className="page-card-heading"><Rocket size={18} /><div><h2>Orbit & microgravity</h2><p>Common free fall creates apparent weightlessness.</p></div></div><div className="atlas-orbit"><div className="atlas-earth"><span>Earth</span></div><i className="atlas-orbit-path" /><div className="atlas-spacecraft"><Rocket size={17} /></div><div className="gravity-arrows"><span>g</span><span>g</span><span>g</span></div></div><p className="atlas-caption">Current model: ideal two-body orbit. Disturbance telemetry remains unconnected.</p></article>
        <article className="atlas-card nv-atlas"><div className="page-card-heading"><Atom size={18} /><div><h2>Four NV orientations</h2><p>Four axial projections constrain one field axis ±B.</p></div></div><svg viewBox="0 0 360 220" role="img" aria-label="Four NV orientation projection diagram"><line x1="180" y1="110" x2="180" y2="25" className="atlas-axis one"/><line x1="180" y1="110" x2="70" y2="180" className="atlas-axis two"/><line x1="180" y1="110" x2="290" y2="180" className="atlas-axis three"/><line x1="180" y1="110" x2="180" y2="210" className="atlas-axis four"/><circle cx="180" cy="110" r="19"/><text x="180" y="115" textAnchor="middle">NV</text><text x="190" y="28">[111]</text><text x="25" y="195">[−111]</text><text x="278" y="195">[1−11]</text><text x="190" y="214">[11−1]</text></svg><p className="atlas-caption">{vectorReconstruction ? `Current candidate |B| ${formatNumber(vectorReconstruction.magnitude, 0)} nT · global sign unresolved.` : 'Run Simulation to reconstruct the current four-axis candidate.'}</p></article>
        <article className="atlas-card signal-atlas"><div className="page-card-heading"><Waves size={18} /><div><h2>ODMR signal formation</h2><p>Microwave frequency becomes photon-count contrast.</p></div></div><div className="signal-steps"><span><Lightbulb size={18}/><b>Optical pump</b></span><i/><span><Radio size={18}/><b>MW sweep</b></span><i/><span><Eye size={18}/><b>Fluorescence</b></span><i/><span><Target size={18}/><b>Fit & CRLB</b></span></div><p className="atlas-caption">{response?.estimation ? `Current |B·n| ${formatNumber(response.estimation.projected_field_magnitude_nt, 0)} nT · fit RMSE ${formatScientific(response.estimation.residual_rmse)}.` : 'Two transition dips around D = 2,870 MHz encode one unsigned axial projection.'}</p></article>
        <article className="atlas-card evidence-atlas"><div className="page-card-heading"><ShieldCheck size={18} /><div><h2>Evidence loop</h2><p>Every result travels with its origin and limitations.</p></div></div><div className="evidence-loop"><span>Config</span><span>Truth</span><span>Acquisition</span><span>Estimate</span><span>Verification</span></div><p className="atlas-caption">{orientationMeasurements.length === 4 ? 'Four channel records are available and remain distinct from simulation truth.' : 'Configuration, raw observables, estimates and truth comparison are separate products.'}</p></article>
      </div>

      <div className="visual-maturity-note"><Info size={17}/><p><strong>How to read these visuals:</strong> diagrams explain relationships; Simulation contains the quantitative experiment. Conceptual geometry is not telemetry, CRLB is not realized error, and model output is not measured hardware data.</p></div>
    </section>
  )
}

function LearnWorkspace() {
  return (
    <section className="workspace-page learn-page" role="tabpanel" id="workspace-panel" aria-labelledby="workspace-tab-learn">
      <div className="workspace-page-hero learn-hero"><div><p className="section-kicker">BQRC learning center</p><h1>Learn the complete measurement chain</h1><p>Begin with frames, orbit and Earth’s field; follow the physics from a diamond defect through eight resonance contributions; finish with vector estimation, uncertainty, evidence and real-hardware readiness.</p></div><div className="workspace-state ready"><GraduationCap size={17}/><span><strong>12 detailed chapters</strong>Equations · method · interpretation · limitations · sources</span></div></div>

      <div className="learning-path" aria-label="Suggested learning path">{['Project & frames','Space environment','NV quantum physics','ODMR spectroscopy','Vector & uncertainty','Evidence & operation'].map((label,index)=><div key={label}><span>0{index+1}</span><strong>{label}</strong></div>)}</div>

      <div className="course-coverage" aria-label="Learning center coverage">
        <div><strong>12</strong><span>guided chapters</span></div>
        <div><strong>17</strong><span>interpreted equations</span></div>
        <div><strong>4 × 2</strong><span>NV axes × transitions</span></div>
        <div><strong>5</strong><span>governed data stages</span></div>
        <p><ShieldCheck size={15}/><span><strong>Completeness rule</strong> Every chapter answers: what it is, how it is calculated or measured, how BQRC uses it, how to interpret it, what can go wrong, and where the evidence comes from.</span></p>
      </div>

      <div className="learn-layout">
        <div className="study-accordion">
          {LEARNING_TOPICS.map((topic, index) => (
            <details key={topic.title} open={index === 0}>
              <summary><span>{String(index + 1).padStart(2,'0')}</span><div><small>{topic.level}</small><strong>{topic.title}</strong><p>{topic.summary}</p></div><ChevronRight size={16}/></summary>
              <div className="study-detail">
                <section className="study-big-idea"><span>Core explanation</span><p>{topic.bigIdea}</p></section>
                <div className="study-method-grid">
                  <section><h4><Workflow size={14}/> How it works</h4><ol>{topic.method.map((step)=><li key={step}>{step}</li>)}</ol></section>
                  <section><h4><FlaskConical size={14}/> Equations, decoded</h4><div className="equation-list">{topic.equations.map((equation)=><div key={equation.expression}><code>{equation.expression}</code><p>{equation.meaning}</p></div>)}</div></section>
                </div>
                <div className="study-meaning-grid">
                  <section><h4><Eye size={14}/> How to interpret it</h4><p>{topic.interpretation}</p></section>
                  <section><h4><Layers3 size={14}/> Where BQRC uses it</h4><p>{topic.projectUse}</p></section>
                </div>
                <section className="study-limits"><h4><AlertCircle size={14}/> Assumptions and common mistakes</h4><ul>{topic.limits.map((limit)=><li key={limit}>{limit}</li>)}</ul></section>
                <div className="study-sources"><span>Traceable sources</span>{topic.references.map((reference)=><a href={reference.url} target={reference.url.startsWith('#') ? undefined : '_blank'} rel={reference.url.startsWith('#') ? undefined : 'noreferrer'} key={reference.label}>{reference.label} <ExternalLink size={11}/></a>)}</div>
              </div>
            </details>
          ))}
        </div>

        <aside className="operator-guide">
          <div className="page-card-heading"><BookMarked size={18}/><div><h2>Complete first experiment</h2><p>Learn, predict, run, inspect and explain.</p></div></div>
          <ol><li><span>1</span>Read chapters 1–8 before changing a value.</li><li><span>2</span>Write down what the default result should qualitatively show.</li><li><span>3</span>Run Simulation and inspect spectrum, photon counts and all four NV axes.</li><li><span>4</span>Separate signed truth, unsigned axial estimates and the ± vector candidate.</li><li><span>5</span>Check fit quality, CRLB assumptions, residual and quality flags.</li><li><span>6</span>Change one input only; predict the direction of change before rerunning.</li><li><span>7</span>Use Architecture to trace every data product, then export the evidence record.</li></ol>
          <div className="interpretation-check"><h3>Before trusting a result</h3><ul><li>What is the measurand?</li><li>Which frame and units apply?</li><li>Is this model, simulation truth or measured data?</li><li>Is the sign observable?</li><li>What does the uncertainty include?</li><li>Which calibration and source version were used?</li></ul></div>
          <div className="glossary"><h3>Essential glossary</h3><dl><div><dt>NV⁻</dt><dd>Negatively charged nitrogen-vacancy spin defect.</dd></div><div><dt>ODMR</dt><dd>Optically detected magnetic resonance.</dd></div><div><dt>IGRF</dt><dd>Reference model of Earth’s main magnetic field.</dd></div><div><dt>Projection</dt><dd>Component of B along one calibrated NV axis.</dd></div><div><dt>CRLB</dt><dd>Conditional lower variance bound, not realized error.</dd></div><div><dt>Measurand</dt><dd>The specific quantity intended to be measured.</dd></div><div><dt>Provenance</dt><dd>Trace of origin, processing and responsibility.</dd></div><div><dt>L0 / L1 / L4</dt><dd>Truth / acquisition / measurement products.</dd></div></dl></div>
        </aside>
      </div>

      <article className="project-documents" id="project-documents"><div className="page-card-heading"><BookOpen size={18}/><div><h2>Project evidence shelf</h2><p>Local baselines and primary or authoritative external references.</p></div></div><div className="document-grid"><div><FileJson size={17}/><strong>REQUIREMENTS.md</strong><p>Stable requirement IDs, scientific states and verification methods.</p></div><div><Layers3 size={17}/><strong>SYSTEM_ARCHITECTURE.md</strong><p>Layering, boundaries and interface rules.</p></div><div><Workflow size={17}/><strong>RUN_CONTRACT_V1.md</strong><p>Config → L0 → L1 → L4 → verification data contract.</p></div><a href="https://www.nasa.gov/centers-and-facilities/glenn/what-is-microgravity/" target="_blank" rel="noreferrer"><Rocket size={17}/><strong>NASA microgravity</strong><p>Free fall, orbit and apparent weightlessness.</p></a><a href="https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field" target="_blank" rel="noreferrer"><Magnet size={17}/><strong>NOAA IGRF-14</strong><p>Official main-field reference model and coefficients.</p></a><a href="https://doi.org/10.1063/5.0066733" target="_blank" rel="noreferrer"><Atom size={17}/><strong>AIP NV review</strong><p>Spin physics, optical readout, ODMR and four orientations.</p></a><a href="https://doi.org/10.1038/s41598-026-50385-6" target="_blank" rel="noreferrer"><Target size={17}/><strong>Vector magnetometry</strong><p>Orientation assignment, four axial projections and the global ± ambiguity.</p></a><a href="https://www.nist.gov/pml/nist-technical-note-1297" target="_blank" rel="noreferrer"><Gauge size={17}/><strong>NIST TN 1297</strong><p>Evaluation and reporting of measurement uncertainty.</p></a><a href="https://www.w3.org/TR/prov-overview/" target="_blank" rel="noreferrer"><GitCompareArrows size={17}/><strong>W3C PROV</strong><p>Provenance entities, activities, agents and traceability.</p></a></div></article>
    </section>
  )
}

function ArchitectureWorkspace() {
  const [architectureView, setArchitectureView] = useState<'scientific' | 'mission'>('scientific')
  const layers = [
    { label: 'Experience', detail: 'React workspace tabs, controls, graphs, evidence and export', icon: <Activity size={18}/> },
    { label: 'API', detail: 'FastAPI validation and /api/v1/nv/odmr/measurement', icon: <Server size={18}/> },
    { label: 'Application', detail: 'Scenario orchestration, deterministic clock and run storage', icon: <Workflow size={18}/> },
    { label: 'Domain', detail: 'Frames, measurements, provenance, uncertainty and quality', icon: <Layers3 size={18}/> },
    { label: 'Scientific models', detail: 'Orbit, IGRF-14, attitude, NV resonance, ODMR and estimator', icon: <Atom size={18}/> },
    { label: 'Infrastructure', detail: 'Configuration, datasets, files and future hardware adapters', icon: <HardDrive size={18}/> },
  ]
  const missionLifecycle = [
    { id: '01', stage: 'Research question', status: 'current', input: 'Mission need, scientific hypothesis and success criteria', output: 'Versioned requirements and measurable acceptance tests', gate: 'Is the measurand and intended use unambiguous?' },
    { id: '02', stage: 'Digital design', status: 'current', input: 'Requirements, interfaces, frames and evidence rules', output: 'Architecture, run contract and traced configuration', gate: 'Can every requirement be verified?' },
    { id: '03', stage: 'Physics simulation', status: 'current', input: 'Orbit, IGRF, attitude, NV and noise models', output: 'L0 truth, L1 acquisition, L4 estimate and errors', gate: 'Do tests and scientific invariants pass?' },
    { id: '04', stage: 'Bench experiment', status: 'next', input: 'Diamond head, laser, microwave, detector and DAQ', output: 'Time-aligned raw spectra with device provenance', gate: 'Does hardware satisfy the L1 acquisition contract?' },
    { id: '05', stage: 'Calibration & V&V', status: 'planned', input: 'Traceable fields, timing, orientation and environmental tests', output: 'Calibration matrices, uncertainty budget and validation report', gate: 'Are accuracy, repeatability and failure modes acceptable?' },
    { id: '06', stage: 'Qualification review', status: 'external', input: 'Safety, thermal, vibration, radiation, EMC and software evidence', output: 'Independent readiness decision and controlled baseline', gate: 'Authorized experts approve use in the intended environment' },
    { id: '07', stage: 'Payload integration', status: 'future', input: 'Qualified sensor, spacecraft interfaces and operations concept', output: 'Integrated payload with power, data, timing and magnetic controls', gate: 'End-to-end functional and interface tests pass' },
    { id: '08', stage: 'Launch campaign', status: 'external', input: 'Approved payload, launch provider and mission procedures', output: 'Deployed spacecraft and recorded as-launched configuration', gate: 'Formal launch and range authority—not a BQRC UI action' },
    { id: '09', stage: 'Commissioning', status: 'future', input: 'Initial telemetry, health data and ground commands', output: 'Verified modes, timing, calibration status and safe limits', gate: 'The sensor is healthy before scientific operation' },
    { id: '10', stage: 'In-orbit sensing', status: 'future', input: 'Local magnetic stimulus plus platform and environment effects', output: 'Timestamped spectra, estimates, quality and housekeeping', gate: 'Only quality-qualified data enters downstream use' },
    { id: '11', stage: 'Space–ground communication', status: 'future', input: 'Packetized observations, metadata and health telemetry', output: 'Authenticated, checked and archived ground products', gate: 'Identity, timing, completeness and integrity are verified' },
    { id: '12', stage: 'Review & improve', status: 'current', input: 'Flight/experiment evidence, anomalies and truth references', output: 'Updated models, requirements, calibration and next experiment', gate: 'Every change creates a new traceable version' },
  ]
  return (
    <section className="workspace-page architecture-page" role="tabpanel" id="workspace-panel" aria-labelledby="workspace-tab-architecture">
      <div className="workspace-page-hero architecture-hero"><div><p className="section-kicker">Flow architecture</p><h1>Follow data without crossing the truth boundary</h1><p>The architecture separates physical truth, sensor observables, algorithm estimates and verification evidence so results remain reproducible and scientifically auditable.</p></div><div className="workspace-state ready"><Network size={17}/><span><strong>Run Contract V1 applied</strong>495 backend tests passed</span></div></div>

      <div className="architecture-view-tabs" role="tablist" aria-label="Architecture view">
        <button type="button" role="tab" aria-selected={architectureView === 'scientific'} aria-controls="scientific-architecture-panel" onClick={() => setArchitectureView('scientific')}><Workflow size={18}/><span><strong>Scientific data flow</strong><small>Truth → acquisition → estimate → evidence</small></span></button>
        <button type="button" role="tab" aria-selected={architectureView === 'mission'} aria-controls="mission-architecture-panel" onClick={() => setArchitectureView('mission')}><Rocket size={18}/><span><strong>Mission lifecycle</strong><small>Platform → experiment → launch → communication</small></span></button>
      </div>

      {architectureView === 'scientific' && <div id="scientific-architecture-panel" role="tabpanel" className="architecture-subview">
      <div className="architecture-layout">
        <article className="layer-stack-card"><div className="page-card-heading"><Layers3 size={18}/><div><h2>System layers</h2><p>Dependencies point inward; UI and hardware do not own scientific truth.</p></div></div><div className="layer-stack">{layers.map((layer,index)=><div key={layer.label}><span>{layer.icon}</span><small>L{index+1}</small><strong>{layer.label}</strong><p>{layer.detail}</p></div>)}</div></article>
        <article className="boundary-card"><div className="page-card-heading"><ShieldCheck size={18}/><div><h2>Scientific truth boundary</h2><p>The most important architectural rule.</p></div></div><div className="boundary-diagram"><div className="truth-zone"><small>Hidden verification domain</small><strong>L0 TruthState</strong><p>Position · attitude · environment · signed reference field</p></div><span><ChevronRight size={18}/></span><div className="stimulus-zone"><small>Physical boundary</small><strong>SensorStimulus</strong><p>Body-frame magnetic vector only</p></div><span><ChevronRight size={18}/></span><div className="observable-zone"><small>Observable domain</small><strong>L1 Acquisition → L4 Measurement</strong><p>Photon counts → unsigned estimate + quality + uncertainty</p></div></div><div className="boundary-rule"><Info size={16}/><p>Truth is used only after estimation to create an ErrorRecord. It is never inserted into sensor data or algorithm inputs.</p></div></article>
      </div>

      <article className="run-flow-card"><div className="page-card-heading"><Workflow size={18}/><div><h2>End-to-end run flow</h2><p>Current software path plus the planned hardware entry point.</p></div></div><div className="architecture-flow">{[
        ['01','ScenarioConfig','Validated inputs + configuration hash'],['02','Clock & orbit','Deterministic time and position'],['03','Environment truth','IGRF field + attitude transform'],['04','Sensor boundary','Simulator today · hardware adapter planned'],['05','ODMRAcquisition','Frequency + photon counts + metadata'],['06','Estimator','Transition fit + |B·n| + CRLB'],['07','Verification','Compare L4 estimate with hidden L0 truth'],['08','Evidence export','Manifest, JSONL/NPZ and browser JSON'],
      ].map((step,index)=><div key={step[0]} className={index===3?'planned-step':''}><span>{step[0]}</span><strong>{step[1]}</strong><p>{step[2]}</p>{index<7&&<i><ChevronRight size={14}/></i>}</div>)}</div></article>

      <div className="artifact-grid"><article><FileJson size={18}/><strong>config.json</strong><p>Frozen scenario and source parameters.</p></article><article><ShieldCheck size={18}/><strong>manifest.json</strong><p>Hashes, versions and run identity.</p></article><article><Database size={18}/><strong>acquisitions.npz</strong><p>Raw L1 photon-count arrays.</p></article><article><Target size={18}/><strong>measurements.jsonl</strong><p>L4 estimates, quality and uncertainty.</p></article><article><GitCompareArrows size={18}/><strong>errors.jsonl</strong><p>Verification-only truth comparisons.</p></article></div>
      </div>}

      {architectureView === 'mission' && <article className="mission-lifecycle-card" id="mission-architecture-panel" role="tabpanel">
        <div className="mission-lifecycle-heading">
          <div className="page-card-heading"><Rocket size={18}/><div><h2>Platform-to-mission lifecycle</h2><p>How BQRC research can progress from a digital study to experiment, qualification, launch, orbital sensing, communication and evidence-driven improvement.</p></div></div>
          <div className="maturity-legend"><span className="current">Current platform</span><span className="next">Next integration</span><span className="planned">Planned BQRC work</span><span className="future">Future mission</span><span className="external">External authority</span></div>
        </div>
        <div className="mission-boundary-note"><AlertCircle size={16}/><p><strong>Readiness boundary:</strong> BQRC currently implements requirements, digital design, simulation, software verification and the review feedback loop. Hardware experiment support is the next integration. Qualification, payload acceptance and launch authorization require separate facilities, evidence and responsible authorities.</p></div>
        <div className="mission-journey" aria-label="BQRC platform to mission lifecycle">
          {missionLifecycle.map((phase, index)=><section className={`mission-phase status-${phase.status}`} key={phase.id}>
            <header><span>{phase.id}</span><div><small>{phase.status === 'current' ? 'Implemented now' : phase.status === 'next' ? 'Next integration' : phase.status === 'external' ? 'External gate' : phase.status === 'planned' ? 'Planned' : 'Future'}</small><h3>{phase.stage}</h3></div>{index < missionLifecycle.length - 1 && <i><ChevronRight size={15}/></i>}</header>
            <dl><div><dt>Input</dt><dd>{phase.input}</dd></div><div><dt>Output</dt><dd>{phase.output}</dd></div><div><dt>Decision gate</dt><dd>{phase.gate}</dd></div></dl>
          </section>)}
        </div>
        <div className="mission-feedback-loop"><RotateCcw size={17}/><p><strong>Closed learning loop:</strong> experiment and mission evidence returns to the requirements and model baseline. BQRC never overwrites history; it creates a new version, reruns verification and records why the model changed.</p></div>
      </article>}
    </section>
  )
}

function App() {
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<WorkspaceTab>('simulation')
  const [form, setForm] = useState<FormState>(DEFAULT_FORM)
  const [response, setResponse] = useState<NVMeasurementResponse | null>(null)
  const [orientationMeasurements, setOrientationMeasurements] = useState<NVOrientationMeasurement[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastRun, setLastRun] = useState<Date | null>(null)
  const [replayCycle, setReplayCycle] = useState(0)
  const abortController = useRef<AbortController | null>(null)

  const chartData = useMemo(() => {
    if (!response) return []

    return response.simulation.frequencies_mhz.map((frequency, index) => ({
      frequency,
      ideal: response.simulation.ideal_fluorescence[index],
      measured: response.simulation.measured_fluorescence[index],
      photons: response.simulation.photon_counts[index],
      residual:
        (response.simulation.measured_fluorescence[index] ?? 0) -
        (response.simulation.ideal_fluorescence[index] ?? 0),
    }))
  }, [response])

  const vectorReconstruction = useMemo(
    () => reconstructVectorFromUnsignedProjections(orientationMeasurements),
    [orientationMeasurements],
  )

  const ensembleChartData = useMemo(() => {
    if (orientationMeasurements.length !== NV_ORIENTATIONS.length) return []

    const frequencies = orientationMeasurements[0].response.simulation.frequencies_mhz
    return frequencies.map((frequency, index) => {
      const row: Record<string, number> = {
        frequency,
        ideal: 0,
        measured: 0,
        photons: 0,
        residual: 0,
      }
      orientationMeasurements.forEach(({ orientation, response: orientationResponse }) => {
        const measured = orientationResponse.simulation.measured_fluorescence[index] ?? 0
        const ideal = orientationResponse.simulation.ideal_fluorescence[index] ?? 0
        const photons = orientationResponse.simulation.photon_counts[index] ?? 0
        row[orientation.id] = measured
        row[`${orientation.id}Photons`] = photons
        row.measured += measured / NV_ORIENTATIONS.length
        row.ideal += ideal / NV_ORIENTATIONS.length
        row.photons += photons
      })
      row.photonMean = row.photons / NV_ORIENTATIONS.length
      row.residual = row.measured - row.ideal
      return row
    })
  }, [orientationMeasurements])

  const displayedChartData = ensembleChartData.length > 0 ? ensembleChartData : chartData

  const transitionWindow = useMemo(() => {
    if (orientationMeasurements.length !== NV_ORIENTATIONS.length) return null
    const transitions = orientationMeasurements.flatMap(({ response: orientationResponse }) => [
      orientationResponse.simulation.lower_mhz,
      orientationResponse.simulation.upper_mhz,
    ])
    const minimum = Math.min(...transitions)
    const maximum = Math.max(...transitions)
    const span = Math.max(maximum - minimum, 0.1)
    const padding = Math.max(span * 0.16, 0.05)
    const sorted = [...transitions].sort((left, right) => left - right)
    const minimumSpacing = Math.min(
      ...sorted.slice(1).map((value, index) => value - sorted[index]),
    )
    return {
      start: minimum - padding,
      end: maximum + padding,
      minimumSpacing,
    }
  }, [orientationMeasurements])

  const vectorVerification = useMemo(() => {
    if (!vectorReconstruction) return null
    const truthMagnitude = vectorMagnitude(form.magneticField)
    const candidateDotTruth = dotVector(vectorReconstruction.candidate, form.magneticField)
    const denominator = vectorReconstruction.magnitude * truthMagnitude
    const axisAngleDeg = denominator === 0
      ? null
      : Math.acos(Math.max(-1, Math.min(1, Math.abs(candidateDotTruth) / denominator))) * 180 / Math.PI
    return {
      truthMagnitude,
      magnitudeResidual: vectorReconstruction.magnitude - truthMagnitude,
      axisAngleDeg,
    }
  }, [form.magneticField, vectorReconstruction])

  const overrideCount = useMemo(() => {
    const scalarKeys: Array<Exclude<keyof FormState, 'magneticField' | 'nvAxis'>> = [
      'frequencyStart',
      'frequencyEnd',
      'samples',
      'contrast',
      'linewidth',
      'photonCount',
      'seed',
    ]
    const scalarOverrides = scalarKeys.filter(
      (key) => form[key] !== DEFAULT_FORM[key],
    ).length
    const vectorOverrides = [...form.magneticField, ...form.nvAxis].filter(
      (value, index) => {
        const defaults = [...DEFAULT_FORM.magneticField, ...DEFAULT_FORM.nvAxis]
        return value !== defaults[index]
      },
    ).length

    return scalarOverrides + vectorOverrides
  }, [form])

  const updateForm = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const handleRun = async () => {
    const validationError = validateForm(form)
    if (validationError) {
      setError(validationError)
      return
    }

    abortController.current?.abort()
    const controller = new AbortController()
    abortController.current = controller
    setIsRunning(true)
    setError(null)

    try {
      const frequencies = createFrequencyGrid(
        form.frequencyStart,
        form.frequencyEnd,
        form.samples,
      )
      const request: NVMeasurementRequest = {
        magnetic_field_nt: form.magneticField,
        nv_axis: form.nvAxis,
        frequencies_mhz: frequencies,
        contrast: form.contrast,
        linewidth_mhz: form.linewidth,
        reference_photon_count: form.photonCount,
        seed: form.seed,
      }

      const [result, crystalMeasurements] = await Promise.all([
        runNVMeasurement(request, controller.signal),
        Promise.all(NV_ORIENTATIONS.map(async (orientation, index) => {
          const seed = (form.seed + index + 1) % (2 ** 32)
          const orientationResponse = await runNVMeasurement({
            ...request,
            nv_axis: orientation.axis,
            seed,
          }, controller.signal)
          return { orientation, response: orientationResponse, seed }
        })),
      ])
      setResponse(result)
      setOrientationMeasurements(crystalMeasurements)
      setLastRun(new Date())
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === 'AbortError') return
      setError(caught instanceof Error ? caught.message : 'The measurement failed')
    } finally {
      if (abortController.current === controller) setIsRunning(false)
    }
  }

  const handleReset = () => {
    abortController.current?.abort()
    setForm(DEFAULT_FORM)
    setResponse(null)
    setOrientationMeasurements([])
    setError(null)
    setLastRun(null)
    setIsRunning(false)
  }

  const handleExport = () => {
    if (!response) return

    const userOverrides = collectParameterOverrides(form)
    const record = {
      schema: 'bqrc-nv-experiment-v3',
      exported_at: new Date().toISOString(),
      default_profile: DEFAULT_PROFILE,
      run_contract: RUN_CONTRACT_PROFILE,
      configuration: form,
      user_overrides: userOverrides,
      provenance_summary: {
        source_classes: ['physics_model', 'validated_model_output', 'bqrc_default', 'engineering_assumption'],
        override_count: userOverrides.length,
        signed_truth_definition: 'Simulator-known directional projection B·n; sign preserved.',
        estimated_field_definition: 'ODMR splitting estimate of |B·n|; sign is not observable in this model.',
        crlb_definition: 'Local lower bound on estimator standard deviation under the stated photon model; not realized error.',
      },
      requirement_references: REQUIREMENT_REFERENCES,
      v1_requirement_traceability: V1_REQUIREMENT_TRACEABILITY,
      baseline_documents: [
        { document: 'SYSTEM_ARCHITECTURE.md', status: 'Initial Locked Architecture' },
        { document: 'REQUIREMENTS.md', status: 'Initial Development Baseline' },
      ],
      four_orientation_analysis: {
        model: 'Four <111> NV orientation families; two ODMR transitions per family.',
        acquisition_mode: 'Four independently seeded simulated two-transition acquisitions.',
        measurements: orientationMeasurements,
        reconstruction: vectorReconstruction,
        interpretation: 'Least-squares branch fit from four unsigned projections. Candidate and opposite vectors are physically indistinguishable without an added sign reference.',
        references: NV_VECTOR_REFERENCES,
      },
      result: response,
    }
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(record, null, 2)], {
        type: 'application/json',
      }),
    )
    const link = document.createElement('a')
    link.href = url
    link.download = `bqrc-nv-experiment-seed-${form.seed}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const signedTruth = response?.simulation.projected_field_nt ?? null
  const estimatedMagnitude = response?.estimation?.projected_field_magnitude_nt ?? null
  const truthMagnitude = signedTruth === null ? null : Math.abs(signedTruth)
  const estimationError =
    estimatedMagnitude === null || truthMagnitude === null
      ? null
      : estimatedMagnitude - truthMagnitude
  const crlb = response?.uncertainty?.crlb_std_nt ?? null
  const resultDigits = crlb === null ? 0 : crlb >= 10 ? 0 : crlb >= 1 ? 1 : 2
  const resonanceSplitting = response
    ? response.simulation.upper_mhz - response.simulation.lower_mhz
    : null
  const uncertaintyScale =
    estimatedMagnitude !== null && truthMagnitude !== null && crlb !== null && crlb > 0
      ? {
          lower: estimatedMagnitude - 3 * crlb,
          upper: estimatedMagnitude + 3 * crlb,
          truthPosition: Math.max(
            0,
            Math.min(100, ((truthMagnitude - (estimatedMagnitude - 3 * crlb)) / (6 * crlb)) * 100),
          ),
        }
      : null
  const photonRange = response
    ? {
        minimum: Math.min(...response.simulation.photon_counts),
        maximum: Math.max(...response.simulation.photon_counts),
      }
    : null

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="BQRC dashboard home" onClick={() => setActiveWorkspaceTab('simulation')}>
          <span className="brand-mark"><Atom size={21} strokeWidth={1.8} /></span>
          <span>
            <strong>BQRC</strong>
            <small>Digital Engineering Platform</small>
          </span>
        </a>
        <div className="topbar-status">
          <span className="status-dot" />
          NV magnetometry workspace
          {overrideCount > 0 && <span className="override-count">{overrideCount} overrides</span>}
          <span className="version-tag">v0.1</span>
        </div>
      </header>

      <nav className="workspace-tabbar" role="tablist" aria-label="BQRC workspaces">
        {([
          { id: 'simulation', label: 'Simulation', note: 'Run & analyze', icon: <FlaskConical size={16} /> },
          { id: 'hardware', label: 'Hardware', note: 'Connect instruments', icon: <Cable size={16} /> },
          { id: 'visualizations', label: 'Visualizations', note: 'See relationships', icon: <Activity size={16} /> },
          { id: 'learn', label: 'Learn', note: 'Study the project', icon: <GraduationCap size={16} /> },
          { id: 'architecture', label: 'Flow architecture', note: 'Trace the system', icon: <Network size={16} /> },
        ] as Array<{ id: WorkspaceTab; label: string; note: string; icon: ReactNode }>).map((tab) => (
          <button
            className={activeWorkspaceTab === tab.id ? 'active' : ''}
            type="button"
            role="tab"
            id={`workspace-tab-${tab.id}`}
            aria-selected={activeWorkspaceTab === tab.id}
            aria-controls="workspace-panel"
            onClick={() => {
              setActiveWorkspaceTab(tab.id)
              window.scrollTo({ top: 0, behavior: 'smooth' })
            }}
            key={tab.id}
          >
            <span>{tab.icon}</span><span><strong>{tab.label}</strong><small>{tab.note}</small></span>
          </button>
        ))}
      </nav>

      <main id="top">
        {activeWorkspaceTab === 'simulation' && <div className="workspace-tab-panel" role="tabpanel" id="workspace-panel" aria-labelledby="workspace-tab-simulation">
        <section className="hero-section">
          <div>
            <div className="overline"><CircleDot size={13} /> NV magnetometry / simulation workspace</div>
            <h1>NV-center ODMR measurement studio</h1>
            <p>
              Simulate photon-limited fluorescence, recover the NV-axis field magnitude,
              and inspect the local information bound in one reproducible workflow.
            </p>
          </div>
          <dl className="hero-spec" aria-label="Current workspace configuration">
            <div><dt>Run mode</dt><dd>Deterministic simulation</dd></div>
            <div><dt>Sensor model</dt><dd>NV ODMR · four axes</dd></div>
            <div><dt>Data class</dt><dd>Software-verified</dd></div>
          </dl>
        </section>

        <section className="environment-story">
          <div className="environment-heading">
            <div>
              <p className="section-kicker">Orbital environment</p>
              <h2>Earth, free fall, and the microgravity environment</h2>
              <p>The BQRC core already contains Earth geometry, orbit, IGRF-14 magnetic field, thermal environment, and an initial residual-microgravity model. This view explains their relationship without presenting unavailable values as live telemetry.</p>
            </div>
            <div className="maturity-badge"><ShieldCheck size={14} /> Core model available · frontend API pending</div>
          </div>

          <div className="environment-grid">
            <div className="earth-stage" aria-label="Conceptual Earth orbit and free-fall visualization">
              <svg viewBox="0 0 620 390" role="img" aria-labelledby="earth-title earth-description">
                <title id="earth-title">Conceptual BQRC orbital environment</title>
                <desc id="earth-description">Earth surrounded by an orbital path carrying a station and BQRC payload in common free fall.</desc>
                <defs>
                  <radialGradient id="earth-ocean" cx="35%" cy="28%">
                    <stop offset="0%" stopColor="#44b8d5" />
                    <stop offset="62%" stopColor="#176ba7" />
                    <stop offset="100%" stopColor="#123e74" />
                  </radialGradient>
                  <radialGradient id="earth-glow">
                    <stop offset="58%" stopColor="#4ec4df" stopOpacity="0" />
                    <stop offset="78%" stopColor="#43b9de" stopOpacity="0.16" />
                    <stop offset="100%" stopColor="#43b9de" stopOpacity="0" />
                  </radialGradient>
                  <filter id="soft-glow"><feGaussianBlur stdDeviation="4" /></filter>
                  <marker id="gravity-tip" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8z" fill="#7bc8e5" /></marker>
                </defs>
                <circle cx="310" cy="198" r="148" fill="url(#earth-glow)" className="earth-halo" />
                <ellipse cx="310" cy="198" rx="270" ry="112" className="orbit-track back-track" />
                <circle cx="310" cy="198" r="103" fill="url(#earth-ocean)" className="earth-sphere" />
                <path d="M240 136c20-27 42-38 70-31l19 18-12 18 17 15-7 23-31 4-19 35-26-5-9-31-18-16zM347 117l31 11 20 29-7 20-28-4-9-22-22-12zM363 214l35 7 13 28-22 34-27-9-12-29zM246 236l22 4 13 31-31 17-24-21z" className="earth-land" />
                <path d="M223 151c46 17 103 17 172-2M210 202c68 19 137 20 204 0M231 250c48 14 98 13 156-3" className="earth-clouds" />
                <path d="M119 122 245 178M501 105 385 174M92 266 230 221" className="gravity-vector" markerEnd="url(#gravity-tip)" />
                <text x="72" y="111" className="space-label">gravity acts here</text>
                <g className="orbital-system">
                  <g className="station-shape" transform="translate(527 180)">
                    <rect x="-24" y="-9" width="48" height="18" rx="4" />
                    <rect x="-54" y="-5" width="26" height="10" className="solar-panel" />
                    <rect x="28" y="-5" width="26" height="10" className="solar-panel" />
                    <path d="M-28 0h-13M28 0h13M0-9v-12M0 9v12" />
                    <circle cx="0" cy="-22" r="4" className="bqrc-node" />
                  </g>
                </g>
                <ellipse cx="310" cy="198" rx="270" ry="112" className="orbit-track front-track" />
                <g className="floating-sample" transform="translate(520 235)"><circle r="7" /><path d="M-12 0h24M0-12v24" /></g>
                <text x="445" y="302" className="space-label">common free fall</text>
                <text x="272" y="194" className="earth-name">EARTH</text>
                <text x="263" y="211" className="earth-subtitle">gravity ≠ zero</text>
              </svg>
              <div className="earth-legend">
                <span><i className="orbit-key" />Conceptual orbital path</span>
                <span><i className="gravity-key" />Gravity direction</span>
                <span><i className="payload-key" />BQRC payload node</span>
              </div>
            </div>

            <div className="microgravity-panel">
              <div className="microgravity-principle">
                <div className="microgravity-value"><strong>0</strong><span>m/s² residual</span></div>
                <div><small>Current ideal baseline model</small><h3>Microgravity is not zero gravity</h3><p>Earth's gravity accelerates the orbiting platform and everything inside it together. Their common free fall creates apparent weightlessness.</p></div>
              </div>

              <div className="disturbance-stack">
                <p>Residual acceleration can come from</p>
                <div><span>Quasi-static bias</span><span>g-jitter</span><span>Structural vibration</span><span>Equipment</span><span>Transient events</span></div>
              </div>

              <div className="effect-flow">
                <div><Activity size={17} /><span><small>Environment</small>Residual acceleration</span></div>
                <ChevronRight size={15} />
                <div><ScanLine size={17} /><span><small>Measurement</small>Accelerometer response</span></div>
                <ChevronRight size={15} />
                <div><Waves size={17} /><span><small>Analysis</small>Time series · FFT · PSD</span></div>
              </div>

              <div className="coupling-note">
                <Info size={17} />
                <p><strong>Current coupling status:</strong> the initial microgravity core returns the ideal two-body free-fall baseline. Disturbance datasets and an environment API are not yet connected to this frontend, and microgravity does not currently modify the NV magnetometry endpoint. Those gaps are shown explicitly rather than filled with invented values.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="workspace-grid">
          <aside className="control-panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">Experiment setup</p>
                <h2>Measurement controls</h2>
              </div>
              <button className="icon-button" type="button" onClick={handleReset} title="Reset experiment">
                <RotateCcw size={17} />
              </button>
            </div>

            <div className="preset-row" aria-label="Experiment presets">
              {PRESETS.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => setForm((current) => ({
                    ...current,
                    magneticField: preset.field,
                    nvAxis: preset.axis,
                  }))}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            <div className={`override-summary ${overrideCount > 0 ? 'active' : ''}`}>
              <ShieldCheck size={15} />
              <span>{overrideCount > 0 ? `${overrideCount} manual parameter overrides active` : 'Default configuration active'}</span>
            </div>

            <div className="default-profile-card">
              <div className="default-profile-heading">
                <Database size={15} />
                <div>
                  <small>Default profile</small>
                  <strong>LEO ISS-like NV V1 · acquisition 0</strong>
                </div>
                <span>Validated model output</span>
              </div>
              <p>Configuration 29373e1e46e52995 · IGRF-14 field at 392.863 km. This is verified simulation truth, not measured flight truth.</p>
              <a href="#evidence-register">View evidence & traceability <ChevronRight size={13} /></a>
            </div>

            <div className="control-group">
              <div className="group-title"><Magnet size={16} /><span>Geometry</span></div>
              <VectorEditor
                label="Magnetic field"
                values={form.magneticField}
                defaults={DEFAULT_FORM.magneticField}
                sourceTag="IGRF output"
                unit="nT"
                onChange={(value) => updateForm('magneticField', value)}
              />
              <VectorEditor
                label="NV axis"
                values={form.nvAxis}
                defaults={DEFAULT_FORM.nvAxis}
                sourceTag="Scenario"
                onChange={(value) => updateForm('nvAxis', value)}
              />
              <p className="field-help"><Info size={13} /> NV axis is normalized by the backend.</p>
            </div>

            <div className="control-group">
              <div className="group-title"><Waves size={16} /><span>Microwave sweep</span></div>
              <div className="input-grid two-column">
                <InputField label="Start" value={form.frequencyStart} unit="MHz" step={0.1} sourceTag="Scenario" overridden={form.frequencyStart !== DEFAULT_FORM.frequencyStart} onChange={(value) => updateForm('frequencyStart', value)} />
                <InputField label="End" value={form.frequencyEnd} unit="MHz" step={0.1} sourceTag="Scenario" overridden={form.frequencyEnd !== DEFAULT_FORM.frequencyEnd} onChange={(value) => updateForm('frequencyEnd', value)} />
                <InputField label="Samples" value={form.samples} min={5} max={5000} step={1} sourceTag="Scenario" overridden={form.samples !== DEFAULT_FORM.samples} onChange={(value) => updateForm('samples', value)} />
                <InputField label="Linewidth" value={form.linewidth} unit="MHz" min={0.01} step={0.1} sourceTag="Scenario" overridden={form.linewidth !== DEFAULT_FORM.linewidth} onChange={(value) => updateForm('linewidth', value)} />
              </div>
            </div>

            <div className="control-group">
              <div className="group-title"><ScanLine size={16} /><span>Detection</span></div>
              <div className="input-grid two-column">
                <InputField label="Contrast" value={form.contrast} min={0.001} max={0.5} step={0.01} sourceTag="Scenario" overridden={form.contrast !== DEFAULT_FORM.contrast} onChange={(value) => updateForm('contrast', value)} />
                <InputField label="Seed" value={form.seed} min={0} step={1} sourceTag="Scenario" overridden={form.seed !== DEFAULT_FORM.seed} onChange={(value) => updateForm('seed', value)} />
                <div className="span-two">
                  <InputField label="Reference photons" value={form.photonCount} min={1} max={1e12} step={10000} unit="counts" sourceTag="Scenario" overridden={form.photonCount !== DEFAULT_FORM.photonCount} onChange={(value) => updateForm('photonCount', value)} />
                </div>
              </div>
            </div>

            {error && <div className="error-banner" role="alert"><AlertCircle size={17} /><span>{error}</span></div>}

            <button className="run-button" type="button" onClick={handleRun} disabled={isRunning}>
              {isRunning ? <LoaderCircle className="spinner" size={18} /> : <Play size={18} fill="currentColor" />}
              {isRunning ? 'Running measurement…' : 'Run measurement'}
              {!isRunning && <ChevronRight size={18} />}
            </button>
          </aside>

          <section className="results-panel">
            <div className="results-header">
              <div>
                <p className="section-kicker">Scientific readout</p>
                <h2>ODMR analysis</h2>
              </div>
              <div className="results-actions">
                <button className="export-button" type="button" onClick={handleExport} disabled={!response}>
                  <Download size={14} /> Export JSON
                </button>
                <div className={`run-status ${response?.fit_success ? 'success' : ''}`}>
                  {response?.fit_success ? <CheckCircle2 size={15} /> : <Activity size={15} />}
                  {response ? (response.fit_success ? 'Fit converged' : 'Fit unavailable') : 'Awaiting run'}
                </div>
              </div>
            </div>

            <div className="metric-grid">
              <MetricCard
                icon={<Target size={19} />}
                eyebrow="Signed truth B·n"
                value={signedTruth === null ? '—' : formatNumber(signedTruth, 0)}
                unit="nT"
                note="Simulator-known directional projection"
                tone="blue"
              />
              <MetricCard
                icon={<Magnet size={19} />}
                eyebrow="Estimated |B·n|"
                value={estimatedMagnitude === null ? '—' : formatNumber(estimatedMagnitude, resultDigits)}
                unit="nT"
                note="Unsigned magnitude inferred from splitting"
                tone="violet"
              />
              <MetricCard
                icon={<Gauge size={19} />}
                eyebrow="Local CRLB σ"
                value={crlb === null ? '—' : formatNumber(crlb, resultDigits)}
                unit="nT"
                note="Theoretical lower bound, not observed error"
                tone="cyan"
              />
              <MetricCard
                icon={<Activity size={19} />}
                eyebrow="Magnitude residual"
                value={estimationError === null ? '—' : formatNumber(estimationError, resultDigits)}
                unit="nT"
                note="Estimate minus absolute simulated truth"
                tone="green"
              />
            </div>

            <div className="quality-strip" aria-label="Scientific quality and maturity summary">
              <div><small>Data origin</small><strong>Simulated sensor response</strong><span>Not measured flight data</span></div>
              <div><small>Estimator state</small><strong>{response ? (response.estimation ? 'Fit converged' : 'Fit unavailable') : 'Awaiting run'}</strong><span>Fit status is not hardware quality</span></div>
              <div><small>Calibration</small><strong>Not applied in V1</strong><span>No hardware calibration claim</span></div>
              <div><small>Model maturity</small><strong>Software-verified</strong><span>Not hardware-validated</span></div>
            </div>

            <div className="pipeline-ribbon" aria-label="Measurement processing pipeline">
              {[
                { label: 'Simulate', icon: <FlaskConical size={15} />, complete: response !== null },
                { label: 'Acquire', icon: <ScanLine size={15} />, complete: response !== null },
                { label: 'Estimate', icon: <GitCompareArrows size={15} />, complete: response?.estimation !== null && response !== null },
                { label: 'Quantify', icon: <Gauge size={15} />, complete: response?.uncertainty !== null && response !== null },
              ].map((step, index) => (
                <div className={step.complete ? 'complete' : ''} key={step.label}>
                  <span>{step.complete ? <CheckCircle2 size={15} /> : step.icon}</span>
                  <p><small>0{index + 1}</small>{step.label}</p>
                </div>
              ))}
            </div>

            <article className="calculation-explorer">
              <div className="calculation-heading">
                <div>
                  <p className="section-kicker">Animated calculation trace</p>
                  <h3>How the NV measurement becomes a field estimate</h3>
                  <p>Conceptual signal flow using the latest backend result. Sequence timing is explanatory—not physical sensor timing.</p>
                </div>
                <button type="button" onClick={() => setReplayCycle((cycle) => cycle + 1)} disabled={!response}>
                  <RotateCcw size={14} /> Replay
                </button>
              </div>

              <div className={`calculation-flow ${response ? 'has-result' : ''}`} key={`${lastRun?.getTime() ?? 0}-${replayCycle}`}>
                <section className="calculation-step step-projection">
                  <div className="step-number">01</div>
                  <div className="step-visual payload-visual" aria-hidden="true">
                    <svg viewBox="0 0 180 112" role="img">
                      <defs>
                        <marker id="arrow-blue" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#1579b9" /></marker>
                        <marker id="arrow-violet" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#735bc8" /></marker>
                      </defs>
                      <g className="payload-body">
                        <rect x="61" y="32" width="58" height="48" rx="8" />
                        <path d="M61 43H28l-14 13 14 13h33M119 43h33l14 13-14 13h-33" />
                        <rect x="77" y="43" width="26" height="26" rx="5" className="diamond-cell" />
                        <path d="m90 47 9 9-9 9-9-9z" className="diamond" />
                      </g>
                      <path d="M15 92 72 67" className="field-arrow" markerEnd="url(#arrow-blue)" />
                      <path d="M89 91V34" className="axis-arrow" markerEnd="url(#arrow-violet)" />
                      <text x="12" y="105">B</text><text x="96" y="29">n̂</text>
                      <circle cx="15" cy="92" r="3" className="flow-particle p1" />
                      <circle cx="35" cy="83" r="2.5" className="flow-particle p2" />
                    </svg>
                  </div>
                  <div className="step-copy"><small>Project geometry</small><strong>B∥ = B · n̂</strong><span>{signedTruth === null ? 'Awaiting simulation' : `${formatNumber(signedTruth, 0)} nT signed truth`}</span></div>
                </section>

                <span className="flow-connector"><i /></span>

                <section className="calculation-step step-splitting">
                  <div className="step-number">02</div>
                  <div className="step-visual energy-visual" aria-hidden="true">
                    <svg viewBox="0 0 180 112">
                      <path d="M28 86H152" className="energy-base" />
                      <path d="M28 31H80M100 31h52" className="energy-upper" />
                      <path d="M62 82V37M118 82V37" className="transition-arrow" />
                      <text x="15" y="34">mₛ ±1</text><text x="15" y="89">mₛ 0</text>
                      <text x="55" y="25">ν−</text><text x="118" y="25">ν+</text>
                    </svg>
                  </div>
                  <div className="step-copy"><small>Zeeman splitting</small><strong>ν± = D ± γₑB∥</strong><span>{response ? `${formatNumber(response.simulation.lower_mhz, 3)} / ${formatNumber(response.simulation.upper_mhz, 3)} MHz` : 'Two transitions around D = 2870 MHz'}</span></div>
                </section>

                <span className="flow-connector"><i /></span>

                <section className="calculation-step step-spectrum">
                  <div className="step-number">03</div>
                  <div className="step-visual dip-visual" aria-hidden="true">
                    <svg viewBox="0 0 180 112">
                      <path d="M12 85H168M22 20V91" className="mini-axis" />
                      <path d="M22 39 C48 39,48 42,59 72 C67 93,77 40,89 40 C103 40,105 92,117 72 C129 43,132 39,164 39" className="dip-line" />
                      <circle cx="63" cy="75" r="3" className="sweep-dot dot-one" />
                      <circle cx="116" cy="75" r="3" className="sweep-dot dot-two" />
                    </svg>
                  </div>
                  <div className="step-copy"><small>ODMR response</small><strong>I(ν) = 1 − C[L− + L+]</strong><span>{formatNumber(form.contrast * 100, 1)}% contrast · {formatNumber(form.linewidth, 2)} MHz linewidth</span></div>
                </section>

                <span className="flow-connector"><i /></span>

                <section className="calculation-step step-photons">
                  <div className="step-number">04</div>
                  <div className="step-visual photon-visual" aria-hidden="true">
                    <div className="laser-beam" />
                    <div className="diamond-chip">NV</div>
                    {Array.from({ length: 12 }, (_, index) => <i key={index} style={{ '--photon-index': index } as CSSProperties} />)}
                    <div className="detector"><ScanLine size={20} /></div>
                  </div>
                  <div className="step-copy"><small>Photon acquisition</small><strong>N ~ Poisson(I · N₀)</strong><span>{photonRange ? `${formatNumber(photonRange.minimum, 0)}–${formatNumber(photonRange.maximum, 0)} counts` : `${formatNumber(form.photonCount, 0)} reference photons`}</span></div>
                </section>

                <span className="flow-connector"><i /></span>

                <section className="calculation-step step-estimate">
                  <div className="step-number">05</div>
                  <div className="step-visual estimate-visual" aria-hidden="true">
                    <div className="estimate-rings"><span /><span /><span /></div>
                    <Target size={31} />
                    <div className="estimate-pulse" />
                  </div>
                  <div className="step-copy"><small>Fit & quantify</small><strong>|B∥| = Δν / (2γₑ)</strong><span>{estimatedMagnitude === null ? 'Unsigned estimate + local CRLB' : `${formatNumber(estimatedMagnitude, resultDigits)} ± ${crlb === null ? '—' : formatNumber(crlb, resultDigits)} nT CRLB`}</span></div>
                </section>
              </div>

              <div className="formula-strip">
                <span><strong>γₑ</strong> 28,024.95 MHz/T</span>
                <span><strong>D</strong> 2,870 MHz</span>
                <span><strong>Δν</strong> {resonanceSplitting === null ? '—' : `${formatNumber(resonanceSplitting, 3)} MHz`}</span>
                <span><strong>Fit RMSE</strong> {response?.estimation ? formatScientific(response.estimation.residual_rmse) : '—'}</span>
                <span><strong>σCRLB</strong> = 1 / √F</span>
              </div>
            </article>

            <article className="nv-vector-lab" aria-labelledby="nv-vector-title">
              <div className="nv-vector-heading">
                <div>
                  <p className="section-kicker">Four-orientation diamond vector lab</p>
                  <h3 id="nv-vector-title">Four NV-axis families · eight ODMR transitions · one ± vector</h3>
                  <p>Each run now evaluates four calibrated diamond ⟨111⟩ directions through the live backend, then combines their independently fitted axial projections.</p>
                </div>
                <span className={orientationMeasurements.length === 4 ? 'vector-ready' : ''}>
                  {orientationMeasurements.length === 4 ? <CheckCircle2 size={13} /> : <LoaderCircle size={13} />}
                  {orientationMeasurements.length === 4 ? '4 / 4 channels fitted' : 'Awaiting acquisition'}
                </span>
              </div>

              <div className="terminology-correction">
                <Info size={17} />
                <p><strong>Scientific terminology:</strong> a diamond may contain many NV defects, but their symmetry axes fall into four crystallographic orientation families. “Two depths” are the two ODMR resonance <em>dips/transitions</em> for <em>mₛ = 0 ↔ mₛ = ±1</em>. Therefore a generic four-family ensemble can contribute up to eight transition lines—not eight physical depth layers. This backend uses the first-order axial model; full transverse-field spin-Hamiltonian fitting remains future work.</p>
              </div>

              <div className="nv-orientation-overview">
                <section className="tetrahedron-panel">
                  <div className="nv-panel-title"><Atom size={17} /><h4>Tetrahedral orientation basis</h4></div>
                  <svg viewBox="0 0 360 238" role="img" aria-labelledby="tetra-title tetra-desc">
                    <title id="tetra-title">Four crystallographic NV orientation families</title>
                    <desc id="tetra-desc">A schematic tetrahedral basis with four axes radiating from a diamond reference point.</desc>
                    <path className="tetra-face rear" d="M180 112 74 184 280 184Z" />
                    <path className="tetra-face front" d="M180 112 180 28 74 184M180 28 280 184" />
                    <line className="nv-axis-line nv-one" x1="180" y1="112" x2="180" y2="28" />
                    <line className="nv-axis-line nv-two" x1="180" y1="112" x2="74" y2="184" />
                    <line className="nv-axis-line nv-three" x1="180" y1="112" x2="280" y2="184" />
                    <line className="nv-axis-line nv-four" x1="180" y1="112" x2="180" y2="218" />
                    <circle className="axis-node nv-one" cx="180" cy="28" r="7" />
                    <circle className="axis-node nv-two" cx="74" cy="184" r="7" />
                    <circle className="axis-node nv-three" cx="280" cy="184" r="7" />
                    <circle className="axis-node nv-four" cx="180" cy="218" r="7" />
                    <circle className="orientation-origin" cx="180" cy="112" r="13" />
                    <text x="180" y="116" textAnchor="middle">V</text>
                    <text className="axis-label" x="190" y="22">NV1 [111]</text>
                    <text className="axis-label" x="18" y="201">NV2 [−111]</text>
                    <text className="axis-label" x="249" y="201">NV3 [1−11]</text>
                    <text className="axis-label" x="190" y="229">NV4 [11−1]</text>
                  </svg>
                  <p>Schematic orientation basis. The crystal-to-body rotation must be calibrated before interpreting these axes as spacecraft coordinates.</p>
                </section>

                <section className="vector-method-panel">
                  <div className="nv-panel-title"><GitCompareArrows size={17} /><h4>Vector reconstruction method</h4></div>
                  <ol>
                    <li><span>01</span><div><strong>Project</strong><p>Each family senses its axial projection <em>Bᵢ = B · n̂ᵢ</em>.</p></div></li>
                    <li><span>02</span><div><strong>Fit two transitions</strong><p><em>νᵢ± ≈ D ± γₑBᵢ</em>; their separation yields <em>|Bᵢ|</em>.</p></div></li>
                    <li><span>03</span><div><strong>Assign four pairs</strong><p>Use a calibrated bias, polarization response, or equivalent orientation-label method.</p></div></li>
                    <li><span>04</span><div><strong>Solve branches</strong><p>Enumerate projection signs and minimize four-axis least-squares residual.</p></div></li>
                    <li><span>05</span><div><strong>Report honestly</strong><p>Without an added sign reference, <em>+B</em> and <em>−B</em> remain indistinguishable.</p></div></li>
                  </ol>
                </section>
              </div>

              <div className="orientation-measurement-grid" aria-label="Four separate NV orientation measurements">
                {NV_ORIENTATIONS.map((orientation) => {
                  const measurement = orientationMeasurements.find((item) => item.orientation.id === orientation.id)
                  const orientationTruth = measurement?.response.simulation.projected_field_nt ?? null
                  const orientationEstimate = measurement?.response.estimation?.projected_field_magnitude_nt ?? null
                  const orientationCrlb = measurement?.response.uncertainty?.crlb_std_nt ?? null
                  const dipChartData = measurement
                    ? measurement.response.simulation.frequencies_mhz.map((frequency, index) => ({
                        frequency,
                        ideal: measurement.response.simulation.ideal_fluorescence[index],
                        measured: measurement.response.simulation.measured_fluorescence[index],
                      }))
                    : []
                  const dipWindow = measurement
                    ? [
                        measurement.response.simulation.lower_mhz - form.linewidth * 2.25,
                        measurement.response.simulation.upper_mhz + form.linewidth * 2.25,
                      ] as [number, number]
                    : null
                  return (
                    <section className={`orientation-measurement ${orientation.colorClass}`} key={orientation.id}>
                      <div className="orientation-card-heading">
                        <span>{orientation.id}</span>
                        <code>{orientation.miller}</code>
                      </div>
                      <p className="axis-vector">n̂ = {formatVector(orientation.axis, 3)}</p>
                      <div className="orientation-value"><small>Fitted |B · n̂|</small><strong>{orientationEstimate === null ? '—' : formatNumber(orientationEstimate, 0)} <span>nT</span></strong></div>
                      <figure className="orientation-dip-figure">
                        <figcaption><span>Two-dip ODMR response</span><small>mₛ = 0 ↔ ±1</small></figcaption>
                        <div className="orientation-dip-chart">
                          {dipChartData.length > 0 && measurement ? (
                            <ResponsiveContainer width="100%" height="100%">
                              <ComposedChart data={dipChartData} margin={{ top: 5, right: 4, left: 4, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="2 4" stroke="rgba(83, 103, 116, 0.13)" vertical={false} />
                                <XAxis dataKey="frequency" type="number" domain={dipWindow ?? ['dataMin', 'dataMax']} allowDataOverflow tickCount={3} tick={{ fill: '#78858d', fontSize: 7 }} tickFormatter={(value) => Number(value).toFixed(1)} axisLine={{ stroke: '#ccd5da' }} tickLine={false} />
                                <YAxis hide domain={['auto', 'auto']} />
                                <ReferenceLine x={measurement.response.simulation.lower_mhz} stroke={orientation.color} strokeDasharray="2 2" opacity={0.72} />
                                <ReferenceLine x={measurement.response.simulation.upper_mhz} stroke={orientation.color} strokeDasharray="2 2" opacity={0.72} />
                                <Line type="monotone" dataKey="ideal" stroke={orientation.color} strokeWidth={1.6} dot={false} isAnimationActive={false} />
                                <Line type="monotone" dataKey="measured" stroke={orientation.color} strokeWidth={.8} dot={false} opacity={0.38} isAnimationActive={false} />
                              </ComposedChart>
                            </ResponsiveContainer>
                          ) : <div className="dip-placeholder"><i /><i /><span>Run acquisition</span></div>}
                        </div>
                        <div className="dip-transition-labels"><span>ν−</span><span>ν+</span></div>
                      </figure>
                      <dl>
                        <div><dt>ν−</dt><dd>{measurement ? `${formatNumber(measurement.response.simulation.lower_mhz, 4)} MHz` : '—'}</dd></div>
                        <div><dt>ν+</dt><dd>{measurement ? `${formatNumber(measurement.response.simulation.upper_mhz, 4)} MHz` : '—'}</dd></div>
                        <div><dt>CRLB σ</dt><dd>{orientationCrlb === null ? '—' : `${formatNumber(orientationCrlb, 0)} nT`}</dd></div>
                        <div><dt>Signed truth</dt><dd>{orientationTruth === null ? '—' : `${formatNumber(orientationTruth, 0)} nT`}</dd></div>
                      </dl>
                      <p className="orientation-seed">Independent simulation seed {measurement?.seed ?? form.seed + NV_ORIENTATIONS.indexOf(orientation) + 1}</p>
                    </section>
                  )
                })}
              </div>

              <div className="combined-vector-grid">
                <section className="combined-vector-summary">
                  <div className="nv-panel-title"><Magnet size={17} /><h4>Combined vector reconstruction</h4></div>
                  {vectorReconstruction ? (
                    <>
                      <p className="combined-magnitude"><span>|B| candidate</span><strong>{formatNumber(vectorReconstruction.magnitude, 0)} <small>nT</small></strong></p>
                      <div className="branch-pair">
                        <div><small>Candidate branch</small><code>+ {formatVector(vectorReconstruction.candidate, 0)} nT</code></div>
                        <div><small>Equivalent branch</small><code>− {formatVector(vectorReconstruction.opposite, 0)} nT</code></div>
                      </div>
                      <p className="branch-rule">Best sign pattern with NV1 fixed positive: {vectorReconstruction.signs.map((sign) => sign > 0 ? '+' : '−').join(' ')} · fit residual {formatNumber(vectorReconstruction.residualRms, 1)} nT</p>
                    </>
                  ) : <div className="vector-empty">Run the measurement to reconstruct the four-axis vector candidate.</div>}
                </section>

                <section className="component-plot">
                  <div className="nv-panel-title"><Activity size={17} /><h4>Reconstructed components</h4></div>
                  {vectorReconstruction ? (
                    <div className="component-bars">
                      {(['Bx', 'By', 'Bz'] as const).map((label, index) => {
                        const value = vectorReconstruction.candidate[index]
                        const maximum = Math.max(...vectorReconstruction.candidate.map((component) => Math.abs(component)), 1)
                        const width = Math.abs(value) / maximum * 46
                        return (
                          <div className="component-row" key={label}>
                            <span>{label}</span>
                            <div className="component-track"><i className={value < 0 ? 'negative' : 'positive'} style={{ left: value < 0 ? `${50 - width}%` : '50%', width: `${width}%` }} /><b /></div>
                            <strong>{formatNumber(value, 0)} nT</strong>
                          </div>
                        )
                      })}
                    </div>
                  ) : <div className="vector-empty">Component bars appear after the four fits.</div>}
                  {vectorVerification && <div className="verification-only"><span>Simulation-only verification</span><strong>|B| residual {formatNumber(vectorVerification.magnitudeResidual, 0)} nT</strong><strong>Axis error {vectorVerification.axisAngleDeg === null ? '—' : `${formatNumber(vectorVerification.axisAngleDeg, 2)}°`}</strong><p>Truth selects neither sign branch; the angle compares the unoriented ± axis only.</p></div>}
                </section>
              </div>

              <section className="transition-map-card">
                <div className="nv-panel-title"><Waves size={17} /><h4>Eight-transition resonance map</h4></div>
                {transitionWindow ? (
                  <>
                    <div className="transition-scale"><span>{formatNumber(transitionWindow.start, 4)} MHz</span><strong>D = 2870 MHz</strong><span>{formatNumber(transitionWindow.end, 4)} MHz</span></div>
                    <div className="transition-rows">
                      {orientationMeasurements.map(({ orientation, response: orientationResponse }) => {
                        const scale = transitionWindow.end - transitionWindow.start
                        const lowerPosition = (orientationResponse.simulation.lower_mhz - transitionWindow.start) / scale * 100
                        const upperPosition = (orientationResponse.simulation.upper_mhz - transitionWindow.start) / scale * 100
                        return (
                          <div className={`transition-row ${orientation.colorClass}`} key={orientation.id}>
                            <span>{orientation.id}</span>
                            <div className="transition-track">
                              <i className="transition-marker lower" style={{ left: `${lowerPosition}%` }}><b>ν−</b></i>
                              <i className="transition-marker upper" style={{ left: `${upperPosition}%` }}><b>ν+</b></i>
                            </div>
                            <code>{formatNumber(orientationResponse.simulation.lower_mhz, 4)} / {formatNumber(orientationResponse.simulation.upper_mhz, 4)}</code>
                          </div>
                        )
                      })}
                    </div>
                    <p className={transitionWindow.minimumSpacing < form.linewidth ? 'resolution-warning' : 'resolution-ok'}><AlertCircle size={14} /> Minimum adjacent-line spacing {formatNumber(transitionWindow.minimumSpacing, 4)} MHz versus {formatNumber(form.linewidth, 3)} MHz linewidth. {transitionWindow.minimumSpacing < form.linewidth ? 'A single ensemble trace would contain overlapping features; the four separately assigned channel fits above remain distinguishable in this demonstrator.' : 'All eight transition locations are separated by more than the configured linewidth.'}</p>
                  </>
                ) : <div className="vector-empty">Eight transition locations appear after acquisition.</div>}
              </section>

              <section className="ensemble-spectrum-card">
                <div className="chart-heading compact-heading">
                  <div><h4>Combined four-axis spectrum · eight dips</h4><p>NV1–NV4 overlaid · two ODMR transitions per orientation family</p></div>
                  <span>Reference aggregate · not a raw ensemble-detector trace</span>
                </div>
                <div className="ensemble-chart">
                  {ensembleChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={ensembleChartData} margin={{ top: 12, right: 12, left: -12, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="4 5" stroke="rgba(113, 142, 177, 0.18)" vertical={false} />
                        <XAxis dataKey="frequency" type="number" domain={transitionWindow ? [transitionWindow.start, transitionWindow.end] : ['dataMin', 'dataMax']} allowDataOverflow tickCount={7} tick={{ fill: '#75849a', fontSize: 10 }} axisLine={{ stroke: '#d8e2ee' }} tickLine={false} unit=" MHz" />
                        <YAxis domain={['auto', 'auto']} tick={{ fill: '#75849a', fontSize: 10 }} axisLine={false} tickLine={false} width={55} />
                        <Tooltip contentStyle={{ borderRadius: 10, border: '1px solid #d9e4ef', fontSize: 11 }} labelFormatter={(value) => `${Number(value).toFixed(3)} MHz`} />
                        <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 10, paddingTop: 9 }} />
                        {orientationMeasurements.flatMap(({ orientation, response: orientationResponse }) => [
                          <ReferenceLine key={`${orientation.id}-lower-aggregate`} x={orientationResponse.simulation.lower_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.7} />,
                          <ReferenceLine key={`${orientation.id}-upper-aggregate`} x={orientationResponse.simulation.upper_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.7} />,
                        ])}
                        <Line type="monotone" dataKey="NV1" name="NV1 measured" stroke="#147ac0" strokeWidth={1} dot={false} opacity={0.48} />
                        <Line type="monotone" dataKey="NV2" name="NV2 measured" stroke="#725cca" strokeWidth={1} dot={false} opacity={0.48} />
                        <Line type="monotone" dataKey="NV3" name="NV3 measured" stroke="#10998d" strokeWidth={1} dot={false} opacity={0.48} />
                        <Line type="monotone" dataKey="NV4" name="NV4 measured" stroke="#d18a2f" strokeWidth={1} dot={false} opacity={0.48} />
                        <Line type="monotone" dataKey="ideal" name="4-channel ideal mean" stroke="#5d7183" strokeWidth={1.4} dot={false} />
                        <Line type="monotone" dataKey="measured" name="4-channel measured mean" stroke="#1f3852" strokeWidth={2.5} dot={false} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : <div className="vector-empty">The four-channel graph appears after acquisition.</div>}
                </div>
              </section>

              <div className="nv-vector-evidence">
                <BookOpen size={16} />
                <span>Peer-reviewed evidence</span>
                {NV_VECTOR_REFERENCES.map((reference) => <a href={reference.url} target="_blank" rel="noreferrer" key={reference.url}>{reference.label} <ExternalLink size={11} /></a>)}
                <code>frontend/src/App.tsx · src/bqrc/api/nv.py</code>
              </div>
            </article>

            <article className="chart-card">
              <div className="chart-heading">
                <div>
                  <h3>{ensembleChartData.length > 0 ? 'Eight-transition fluorescence spectrum' : 'Fluorescence spectrum'}</h3>
                  <p>{ensembleChartData.length > 0 ? 'Four-family normalized aggregate with eight resonance contributions' : 'Normalized ODMR response across the microwave sweep'}</p>
                </div>
                {lastRun && <span>Updated {lastRun.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>}
              </div>

              <div className="chart-area">
                {displayedChartData.length > 0 && response ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={displayedChartData} margin={{ top: 14, right: 12, left: -12, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="4 5" stroke="rgba(113, 142, 177, 0.18)" vertical={false} />
                      <XAxis dataKey="frequency" type="number" domain={['dataMin', 'dataMax']} tickCount={7} tick={{ fill: '#75849a', fontSize: 11 }} axisLine={{ stroke: '#d8e2ee' }} tickLine={false} unit=" MHz" />
                      <YAxis domain={['auto', 'auto']} tick={{ fill: '#75849a', fontSize: 11 }} axisLine={false} tickLine={false} width={55} />
                      <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #d9e4ef', boxShadow: '0 12px 32px rgba(27, 48, 78, 0.12)', fontSize: 12 }} labelFormatter={(value) => `${Number(value).toFixed(3)} MHz`} />
                      <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
                      {orientationMeasurements.length > 0 ? orientationMeasurements.flatMap(({ orientation, response: orientationResponse }) => [
                        <ReferenceLine key={`${orientation.id}-lower-main`} x={orientationResponse.simulation.lower_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.72} />,
                        <ReferenceLine key={`${orientation.id}-upper-main`} x={orientationResponse.simulation.upper_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.72} />,
                      ]) : [
                        <ReferenceLine key="primary-lower" x={response.simulation.lower_mhz} stroke="#7359d9" strokeDasharray="4 4" />,
                        <ReferenceLine key="primary-upper" x={response.simulation.upper_mhz} stroke="#7359d9" strokeDasharray="4 4" />,
                      ]}
                      <Line type="monotone" dataKey="ideal" name={ensembleChartData.length > 0 ? 'Four-family ideal mean' : 'Ideal fluorescence'} stroke="#0d73c9" strokeWidth={2.4} dot={false} activeDot={{ r: 4 }} />
                      <Scatter dataKey="measured" name={ensembleChartData.length > 0 ? 'Four-family measured mean' : 'Measured fluorescence'} fill="#15b5a5" opacity={0.58} />
                    </ComposedChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-chart">
                    <div className="empty-icon"><ScanLine size={29} /></div>
                    <h3>Ready to acquire a spectrum</h3>
                    <p>Configure the experiment and run a measurement to populate the scientific readout.</p>
                  </div>
                )}
              </div>
            </article>

            <div className="analysis-grid">
              <article className="analysis-card">
                <div className="chart-heading compact-heading">
                  <div>
                    <h3>{ensembleChartData.length > 0 ? 'Four-family fluorescence residuals' : 'Fluorescence residuals'}</h3>
                    <p>{ensembleChartData.length > 0 ? 'Measured aggregate minus ideal aggregate at each sweep point' : 'Measured minus ideal response at each sweep point'}</p>
                  </div>
                  <GitCompareArrows size={18} />
                </div>
                <div className="mini-chart">
                  {displayedChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={displayedChartData} margin={{ top: 10, right: 8, left: -20, bottom: 2 }}>
                        <CartesianGrid strokeDasharray="3 5" stroke="rgba(113, 142, 177, 0.16)" vertical={false} />
                        <XAxis dataKey="frequency" type="number" domain={['dataMin', 'dataMax']} tickCount={5} tick={{ fill: '#8291a1', fontSize: 9 }} axisLine={{ stroke: '#d8e2ee' }} tickLine={false} />
                        <YAxis tick={{ fill: '#8291a1', fontSize: 9 }} axisLine={false} tickLine={false} width={50} tickFormatter={(value) => Number(value).toExponential(1)} />
                        <Tooltip contentStyle={{ borderRadius: 10, border: '1px solid #d9e4ef', fontSize: 11 }} labelFormatter={(value) => `${Number(value).toFixed(3)} MHz`} />
                        <ReferenceLine y={0} stroke="#8799aa" />
                        <Bar dataKey="residual" name="Fluorescence residual" fill="#6f5dcc" opacity={0.76} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : <div className="mini-empty">Residual analysis appears after acquisition.</div>}
                </div>
              </article>

              <article className="analysis-card">
                <div className="chart-heading compact-heading">
                  <div>
                    <h3>{ensembleChartData.length > 0 ? 'Eight-transition photon-count trace' : 'Photon-count trace'}</h3>
                    <p>{ensembleChartData.length > 0 ? 'Four separate orientation traces plus their channel-normalized mean' : 'Raw Poisson counts retained across frequency'}</p>
                  </div>
                  <Database size={18} />
                </div>
                <div className="mini-chart">
                  {displayedChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={displayedChartData} margin={{ top: 10, right: 8, left: -12, bottom: 2 }}>
                        <defs>
                          <linearGradient id="photon-fill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#11a89c" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="#11a89c" stopOpacity={0.03} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 5" stroke="rgba(113, 142, 177, 0.16)" vertical={false} />
                        <XAxis dataKey="frequency" type="number" domain={['dataMin', 'dataMax']} tickCount={5} tick={{ fill: '#8291a1', fontSize: 9 }} axisLine={{ stroke: '#d8e2ee' }} tickLine={false} />
                        <YAxis tick={{ fill: '#8291a1', fontSize: 9 }} axisLine={false} tickLine={false} width={58} tickFormatter={(value) => `${Math.round(Number(value) / 1000)}k`} />
                        <Tooltip contentStyle={{ borderRadius: 10, border: '1px solid #d9e4ef', fontSize: 11 }} labelFormatter={(value) => `${Number(value).toFixed(3)} MHz`} />
                        {orientationMeasurements.flatMap(({ orientation, response: orientationResponse }) => [
                          <ReferenceLine key={`${orientation.id}-lower-photons`} x={orientationResponse.simulation.lower_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.52} />,
                          <ReferenceLine key={`${orientation.id}-upper-photons`} x={orientationResponse.simulation.upper_mhz} stroke={orientation.color} strokeDasharray="3 4" opacity={0.52} />,
                        ])}
                        {orientationMeasurements.length > 0 && <>
                          <Line type="monotone" dataKey="NV1Photons" name="NV1 photons" stroke="#147ac0" strokeWidth={1} dot={false} opacity={0.48} />
                          <Line type="monotone" dataKey="NV2Photons" name="NV2 photons" stroke="#725cca" strokeWidth={1} dot={false} opacity={0.48} />
                          <Line type="monotone" dataKey="NV3Photons" name="NV3 photons" stroke="#10998d" strokeWidth={1} dot={false} opacity={0.48} />
                          <Line type="monotone" dataKey="NV4Photons" name="NV4 photons" stroke="#d18a2f" strokeWidth={1} dot={false} opacity={0.48} />
                        </>}
                        <Area type="monotone" dataKey={ensembleChartData.length > 0 ? 'photonMean' : 'photons'} name={ensembleChartData.length > 0 ? 'Four-channel photon mean' : 'Photon counts'} stroke="#0a9389" strokeWidth={1.8} fill="url(#photon-fill)" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : <div className="mini-empty">Raw photon statistics appear after acquisition.</div>}
                </div>
              </article>
            </div>

            <div className="engineering-visuals">
              <article className="range-card">
                <div className="detail-title"><Waves size={17} /><h3>Resonance splitting</h3></div>
                {response && resonanceSplitting !== null ? (
                  <>
                    <div className="resonance-scale">
                      <span className="scale-line" />
                      <span className="resonance-marker lower" style={{ left: `${((response.simulation.lower_mhz - form.frequencyStart) / (form.frequencyEnd - form.frequencyStart)) * 100}%` }}><i />ν−</span>
                      <span className="zero-marker" style={{ left: `${((2870 - form.frequencyStart) / (form.frequencyEnd - form.frequencyStart)) * 100}%` }}>D</span>
                      <span className="resonance-marker upper" style={{ left: `${((response.simulation.upper_mhz - form.frequencyStart) / (form.frequencyEnd - form.frequencyStart)) * 100}%` }}><i />ν+</span>
                    </div>
                    <div className="range-labels"><span>{formatNumber(response.simulation.lower_mhz, 3)} MHz</span><strong>Δν {formatNumber(resonanceSplitting, 3)} MHz</strong><span>{formatNumber(response.simulation.upper_mhz, 3)} MHz</span></div>
                  </>
                ) : <div className="visual-empty">Transition markers await a valid spectrum.</div>}
              </article>

              <article className="range-card">
                <div className="detail-title"><Gauge size={17} /><h3>Local precision scale</h3></div>
                {uncertaintyScale && estimatedMagnitude !== null && crlb !== null ? (
                  <>
                    <div className="uncertainty-scale">
                      <span className="uncertainty-band" />
                      <span className="estimate-marker" title="Estimated magnitude" />
                      <span className="truth-marker" style={{ left: `${uncertaintyScale.truthPosition}%` }} title="Absolute simulation truth" />
                    </div>
                    <div className="range-labels"><span>{formatNumber(uncertaintyScale.lower, resultDigits)} nT</span><strong>estimate ± 3σCRLB</strong><span>{formatNumber(uncertaintyScale.upper, resultDigits)} nT</span></div>
                    <div className="scale-legend"><span><i className="truth-key" />|truth|</span><span><i className="estimate-key" />estimate</span><em>Scale only—not a confidence interval</em></div>
                  </>
                ) : <div className="visual-empty">A locally identifiable fit is required.</div>}
              </article>
            </div>

            <div className="detail-grid">
              <article className="detail-card">
                <div className="detail-title"><CircleDot size={17} /><h3>Resonance fit</h3></div>
                <dl>
                  <div><dt>Lower transition</dt><dd>{response ? `${formatNumber(response.simulation.lower_mhz, 4)} MHz` : '—'}</dd></div>
                  <div><dt>Upper transition</dt><dd>{response ? `${formatNumber(response.simulation.upper_mhz, 4)} MHz` : '—'}</dd></div>
                  <div><dt>Fit RMSE</dt><dd>{response?.estimation ? formatScientific(response.estimation.residual_rmse) : '—'}</dd></div>
                </dl>
              </article>
              <article className="detail-card">
                <div className="detail-title"><Gauge size={17} /><h3>Information limit</h3></div>
                <dl>
                  <div><dt>Fisher information</dt><dd>{response?.uncertainty ? `${formatScientific(response.uncertainty.fisher_information_per_nt_squared)} nT⁻²` : '—'}</dd></div>
                  <div><dt>Locally identifiable</dt><dd>{response?.uncertainty ? (response.uncertainty.identifiable_locally ? 'Yes' : 'No') : '—'}</dd></div>
                  <div><dt>Photon samples</dt><dd>{response ? formatNumber(response.simulation.photon_counts.length, 0) : '—'}</dd></div>
                </dl>
              </article>
            </div>

            <article className="provenance-card">
              <div className="provenance-heading">
                <div className="detail-title"><BookOpen size={17} /><h3>Model provenance & maturity</h3></div>
                <span>Simulation model · V1 implementation</span>
              </div>
              <div className="provenance-grid">
                <div><small>Scientific source</small><strong>Python BQRC NV/ODMR pipeline</strong><p>Results are returned by the integrated measurement endpoint—not generated in the browser.</p><a href="https://doi.org/10.1063/5.0066733" target="_blank" rel="noreferrer">NV/ODMR reference <ExternalLink size={11} /></a></div>
                <div><small>Measurement model</small><strong>Two-resonance ODMR + Poisson counts</strong><p>Deterministic seed {form.seed}; fit uses raw simulated photon counts.</p><a href="https://tf.nist.gov/general/pdf/3216.pdf" target="_blank" rel="noreferrer">NIST shot-noise basis <ExternalLink size={11} /></a></div>
                <div><small>API provenance</small><strong>/api/v1/nv/odmr/measurement</strong><p>Signed simulation truth is kept separate from the unsigned spectral estimate.</p></div>
                <div><small>Validation status</small><strong>Software-verified, not hardware-validated</strong><p>This display demonstrates model behaviour and does not establish physical validation.</p></div>
              </div>
              <div className="constant-reference-strip">
                <div><span>Physics constant</span><strong>D = 2,870 MHz</strong><a href="https://doi.org/10.1063/5.0066733" target="_blank" rel="noreferrer">peer-reviewed source <ExternalLink size={11} /></a></div>
                <div><span>Physics constant</span><strong>γₑ/2π = 28,024.95 MHz T⁻¹</strong><a href="https://physics.nist.gov/cgi-bin/cuu/Value?gammaebar%7Csearch_for=gyromagnetic+ratio" target="_blank" rel="noreferrer">NIST CODATA <ExternalLink size={11} /></a></div>
                <div><span>Editable profile</span><strong>{PARAMETER_PROVENANCE.length} traced defaults</strong><a href="#evidence-register">requirement evidence <ChevronRight size={11} /></a></div>
              </div>
            </article>

            <article className="run-contract-card">
              <div className="run-contract-heading">
                <div>
                  <p className="section-kicker">Applied backend contract</p>
                  <div className="detail-title"><GitCompareArrows size={18} /><h3>Run Contract V1 data lineage</h3></div>
                </div>
                <span><CheckCircle2 size={13} /> 495 tests passed</span>
              </div>
              <p className="run-contract-intro">The contract keeps hidden ground truth out of sensor and estimator objects while preserving a reproducible path from configuration to verification.</p>
              <div className="contract-flow" aria-label="Run Contract V1 processing levels">
                {RUN_CONTRACT_PROFILE.stages.map((stage) => (
                  <div className="contract-stage" key={stage.level}>
                    <small>{stage.level}</small>
                    <strong>{stage.type}</strong>
                    <p>{stage.detail}</p>
                  </div>
                ))}
              </div>
              <div className="scenario-reference-grid">
                <div><small>Scenario</small><strong>leo-iss-like-nv-v1</strong><span>2027-07-18 10:00 UTC · 90 min · 10 s step</span></div>
                <div><small>Orbit</small><strong>6,771 km radius · 51.6°</strong><span>Ideal circular two-body model</span></div>
                <div><small>Acquisition 0</small><strong>|B| = 24,031.376 nT</strong><span>B·n = +8,304.235 nT · altitude 392.863 km</span></div>
                <div><small>Reproducibility</small><strong>29373e1e46e52995</strong><span>Configuration hash · master seed 2027</span></div>
              </div>
              <div className="truth-boundary-note">
                <ShieldCheck size={17} />
                <p><strong>Truth boundary:</strong> sensors receive only a body-frame physical stimulus. L1 acquisitions contain photon counts and metadata—not ideal spectra or true field labels. Verification compares L4 estimates with L0 truth outside the sensor and algorithm layers.</p>
              </div>
              <div className="contract-references">
                <span>Repository evidence</span>
                <code>docs/design/RUN_CONTRACT_V1.md</code>
                <code>configs/scenarios/leo_iss_like_nv_v1.json</code>
                <code>tests/scientific/test_run_nv_scenario.py</code>
              </div>
            </article>

            <article className="v1-traceability-card" aria-labelledby="v1-traceability-title">
              <div className="v1-traceability-heading">
                <div>
                  <p className="section-kicker">REQUIREMENTS.md · V1 baseline</p>
                  <div className="detail-title"><ShieldCheck size={18} /><h3 id="v1-traceability-title">V1 requirement verification matrix</h3></div>
                </div>
                <div className="v1-status-summary" aria-label="Requirement status counts">
                  <span className="v1-status status-verified">13 verified</span>
                  <span className="v1-status status-implemented">4 implemented</span>
                  <span className="v1-status status-partial">1 partial</span>
                  <span className="v1-status status-planned">2 planned</span>
                </div>
              </div>
              <p className="v1-traceability-intro">Every scoped V1 requirement is shown with its present state and concrete verification evidence. Planned and partial work remains visible rather than being presented as complete.</p>
              <div className="v1-requirement-grid">
                {V1_REQUIREMENT_TRACEABILITY.map((item) => (
                  <section className="v1-requirement-item" key={item.id}>
                    <div className="v1-requirement-id">
                      <code>{item.id}</code>
                      <span className={`v1-status status-${item.status.toLowerCase()}`}>{item.status}</span>
                    </div>
                    <h4>{item.title}</h4>
                    <p>{item.note}</p>
                    <dl>
                      <div><dt>Method</dt><dd>{item.verification}</dd></div>
                      <div><dt>Evidence</dt><dd><code>{item.evidence}</code></dd></div>
                    </dl>
                  </section>
                ))}
              </div>
            </article>

            <article className="evidence-register" id="evidence-register">
              <div className="evidence-register-heading">
                <div>
                  <p className="section-kicker">SYSTEM_ARCHITECTURE.md · REQUIREMENTS.md</p>
                  <div className="detail-title"><BookOpen size={18} /><h3>Requirement evidence & traceability register</h3></div>
                </div>
                <span>Authoritative links · honest maturity</span>
              </div>
              <p className="evidence-intro">Each frontend area maps to stable BQRC requirement IDs, repository evidence, and external scientific or engineering baselines. Status describes this implementation—it does not claim that a linked standard is fully implemented.</p>
              <div className="evidence-grid">
                {REQUIREMENT_REFERENCES.map((reference) => (
                  <section className="evidence-item" key={reference.id}>
                    <div className="evidence-item-heading">
                      <span className="area-index">{reference.id}</span>
                      <span className={`evidence-status status-${reference.status.toLowerCase()}`}>{reference.status}</span>
                    </div>
                    <h4>{reference.area}</h4>
                    <div className="requirement-id-list" aria-label={`${reference.area} requirement identifiers`}>
                      {reference.requirements.map((requirement) => <code key={requirement}>{requirement}</code>)}
                    </div>
                    <strong>{reference.source}</strong>
                    <p>{reference.note}</p>
                    <div className="evidence-links">
                      {reference.links.map((link) => (
                        <a href={link.url} target="_blank" rel="noreferrer" key={link.url}>
                          {link.label} <ExternalLink size={11} />
                        </a>
                      ))}
                    </div>
                    {reference.localReferences && (
                      <div className="local-references">
                        {reference.localReferences.map((path) => <code key={path}>{path}</code>)}
                      </div>
                    )}
                  </section>
                ))}
              </div>
              <div className="evidence-legend">
                <span><i className="source-physics" /> Physics model: externally sourced constant or relationship</span>
                <span><i className="source-output" /> Validated model output: reproducible result from a verified software path</span>
                <span><i className="source-default" /> BQRC default: software-tested model setting</span>
                <span><i className="source-assumption" /> Engineering assumption: controlled scenario, not measured truth</span>
                <span><i className="source-override" /> User override: exported with original and changed values</span>
              </div>
            </article>

            <div className="science-note">
              <Info size={18} />
              <p><strong>Interpretation guardrail:</strong> ODMR line splitting is symmetric under sign reversal, so the estimator reports only <em>|B·n|</em>. The signed <em>B·n</em> above is simulation truth. CRLB σ is a local best-case precision bound under the stated photon model; it is not the actual error of this realization.</p>
            </div>
          </section>
        </section>
        </div>}
        {activeWorkspaceTab === 'hardware' && <HardwareWorkspace />}
        {activeWorkspaceTab === 'visualizations' && <VisualizationWorkspace response={response} orientationMeasurements={orientationMeasurements} vectorReconstruction={vectorReconstruction} />}
        {activeWorkspaceTab === 'learn' && <LearnWorkspace />}
        {activeWorkspaceTab === 'architecture' && <ArchitectureWorkspace />}
      </main>

      <footer>
        <span>BQRC · Quantum Resilient Navigation Research</span>
        <span>Deterministic seed · Poisson photon model · NV ODMR</span>
      </footer>
    </div>
  )
}

export default App
