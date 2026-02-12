import {
  Card,
  CardContent,
  Chip,
  Grid2,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'
import api from '../api/client'

type TrafficLight = 'GREEN' | 'YELLOW' | 'RED'

interface AgingMachine {
  machine_id: string
  machine_number: string
  refurb_site: string
  status: string
  stage_days: number
  total_process_days: number
  estimated_market_value_eur?: number
  traffic_light: TrafficLight
}

interface OperationsDashboard {
  top_kpis: {
    total_machines_in_process: number
    average_days_since_arrival: number
    machines_over_30_days: number
    machines_over_45_days: number
  }
  transport: {
    average_transport_days: number
    underway_count: number
    oldest_transports: Array<{
      machine_id: string
      machine_number: string
      refurb_site: string
      transport_days: number
      total_process_days: number
      traffic_light: TrafficLight
    }>
  }
  intake_assessment: {
    average_arrival_to_workshop_days: number
    intake_assessment_count: number
    highlighted_machines: AgingMachine[]
  }
  workshop: {
    average_workshop_to_done_days: number
    refurbishment_count: number
    highlighted_machines: AgingMachine[]
  }
}

const lightColor: Record<TrafficLight, 'success' | 'warning' | 'error'> = {
  GREEN: 'success',
  YELLOW: 'warning',
  RED: 'error',
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<OperationsDashboard | null>(null)

  useEffect(() => {
    const load = async () => {
      const { data } = await api.get<OperationsDashboard>('/dashboard/operations')
      setDashboard(data)
    }
    void load()
  }, [])

  if (!dashboard) return <Typography>Lade Transparenz-Cockpit...</Typography>

  return (
    <Grid2 container spacing={2}>
      <Grid2 size={12}>
        <Typography variant="h5">Operatives Transparenz-Cockpit</Typography>
      </Grid2>

      <Grid2 size={3}><Card><CardContent><Typography variant="subtitle2">Gesamtmaschinen im Prozess</Typography><Typography variant="h4">{dashboard.top_kpis.total_machines_in_process}</Typography></CardContent></Card></Grid2>
      <Grid2 size={3}><Card><CardContent><Typography variant="subtitle2">Ø Tage seit Ankunft</Typography><Typography variant="h4">{dashboard.top_kpis.average_days_since_arrival}</Typography></CardContent></Card></Grid2>
      <Grid2 size={3}><Card><CardContent><Typography variant="subtitle2">Maschinen &gt; 30 Tage</Typography><Typography variant="h4">{dashboard.top_kpis.machines_over_30_days}</Typography></CardContent></Card></Grid2>
      <Grid2 size={3}><Card><CardContent><Typography variant="subtitle2">Maschinen &gt; 45 Tage</Typography><Typography variant="h4">{dashboard.top_kpis.machines_over_45_days}</Typography></CardContent></Card></Grid2>

      <Grid2 size={4}>
        <Card sx={{ height: 520 }}>
          <CardContent>
            <Typography variant="h6">Transport</Typography>
            <Typography>Ø Transportdauer: {dashboard.transport.average_transport_days} Tage</Typography>
            <Typography>UNDERWAY: {dashboard.transport.underway_count}</Typography>
            <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 380 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Maschine</TableCell>
                    <TableCell>Standort</TableCell>
                    <TableCell align="right">Tage</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboard.transport.oldest_transports.map((machine) => (
                    <TableRow key={machine.machine_id}>
                      <TableCell>{machine.machine_number}</TableCell>
                      <TableCell>{machine.refurb_site}</TableCell>
                      <TableCell align="right">{machine.transport_days}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid2>

      <Grid2 size={4}>
        <Card sx={{ height: 520 }}>
          <CardContent>
            <Typography variant="h6">Eingang & Bewertung</Typography>
            <Typography>Ø Ankunft → Werkstattstart: {dashboard.intake_assessment.average_arrival_to_workshop_days} Tage</Typography>
            <Typography>INTAKE_ASSESSMENT: {dashboard.intake_assessment.intake_assessment_count}</Typography>
            <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 380 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Maschine</TableCell>
                    <TableCell align="right">Tage in Phase</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboard.intake_assessment.highlighted_machines.map((machine) => (
                    <TableRow key={machine.machine_id}>
                      <TableCell>{machine.machine_number}</TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${machine.stage_days} Tage`}
                          color={machine.stage_days > 20 ? 'error' : machine.stage_days > 10 ? 'warning' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid2>

      <Grid2 size={4}>
        <Card sx={{ height: 520 }}>
          <CardContent>
            <Typography variant="h6">Werkstatt</Typography>
            <Typography>Ø Werkstattstart → Fertig: {dashboard.workshop.average_workshop_to_done_days} Tage</Typography>
            <Typography>REFURBISHMENT: {dashboard.workshop.refurbishment_count}</Typography>
            <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 380 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Maschine</TableCell>
                    <TableCell align="right">Tage in Phase</TableCell>
                    <TableCell align="right">Ampel</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboard.workshop.highlighted_machines.map((machine) => (
                    <TableRow key={machine.machine_id}>
                      <TableCell>{machine.machine_number}</TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${machine.stage_days} Tage`}
                          color={machine.stage_days > 30 ? 'error' : machine.stage_days > 20 ? 'warning' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right"><Chip label={machine.traffic_light} color={lightColor[machine.traffic_light]} size="small" /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid2>
    </Grid2>
  )
}
