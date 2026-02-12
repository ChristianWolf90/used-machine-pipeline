export type MachineStatus = 'UNDERWAY' | 'INTAKE_ASSESSMENT' | 'REFURBISHMENT' | 'SALE_READY'

export interface Machine {
  id: string
  machine_number: string
  type_model?: string
  value_class?: 'A' | 'B' | 'C'
  estimated_market_value_eur?: number
  rental_origin_site?: string
  refurb_site: 'Passau' | 'Andernach' | 'Welzow'
  status: MachineStatus
  dt_rental_exit: string
  dt_arrival_refurb?: string
  dt_workshop_start?: string
  dt_tech_done?: string
  dt_sale_ready?: string
  notes?: string
  created_at: string
  updated_at: string
  total_process_days: number
  traffic_light: 'GREEN' | 'YELLOW' | 'RED'
}

export interface LoginResponse {
  access_token: string
  token_type: string
  role: 'Admin' | 'SiteUser'
  site?: 'Passau' | 'Andernach' | 'Welzow'
}
