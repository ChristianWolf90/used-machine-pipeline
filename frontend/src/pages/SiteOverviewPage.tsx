import { Chip, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import api from '../api/client'

type TrafficLight = 'GREEN' | 'YELLOW' | 'RED'

interface SiteWorklistItem {
  machine_id: string
  machine_number: string
  refurb_site: string
  status: string
  total_process_days: number
  estimated_market_value_eur?: number
  traffic_light: TrafficLight
}

const statuses = ['', 'UNDERWAY', 'INTAKE_ASSESSMENT', 'REFURBISHMENT', 'SALE_READY']
const sites = ['', 'Passau', 'Andernach', 'Welzow']

const lightColor: Record<TrafficLight, 'success' | 'warning' | 'error'> = {
  GREEN: 'success',
  YELLOW: 'warning',
  RED: 'error',
}

export default function SiteOverviewPage() {
  const [items, setItems] = useState<SiteWorklistItem[]>([])
  const [site, setSite] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => {
    const load = async () => {
      const { data } = await api.get<{ items: SiteWorklistItem[] }>('/dashboard/site-worklist', { params: { site: site || undefined, status: status || undefined } })
      setItems(data.items)
    }
    void load()
  }, [site, status])

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Standort Übersicht</Typography>
      <Stack direction="row" spacing={2}>
        <TextField select label="Standort" value={site} onChange={(event) => setSite(event.target.value)} sx={{ minWidth: 180 }}>
          {sites.map((entry) => <MenuItem key={entry} value={entry}>{entry || 'Alle'}</MenuItem>)}
        </TextField>
        <TextField select label="Status" value={status} onChange={(event) => setStatus(event.target.value)} sx={{ minWidth: 220 }}>
          {statuses.map((entry) => <MenuItem key={entry} value={entry}>{entry || 'Alle'}</MenuItem>)}
        </TextField>
      </Stack>

      <TableContainer component={Paper} sx={{ maxHeight: 620 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Maschine</TableCell>
              <TableCell>Standort</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Ampel</TableCell>
              <TableCell align="right">Marktwert (€)</TableCell>
              <TableCell align="right">Gesamttage</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.machine_id}>
                <TableCell>{item.machine_number}</TableCell>
                <TableCell>{item.refurb_site}</TableCell>
                <TableCell>{item.status}</TableCell>
                <TableCell><Chip label={item.traffic_light} color={lightColor[item.traffic_light]} size="small" /></TableCell>
                <TableCell align="right">{item.estimated_market_value_eur ? item.estimated_market_value_eur.toLocaleString('de-DE') : '-'}</TableCell>
                <TableCell align="right">{item.total_process_days}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  )
}
