import { Card, CardContent, Grid2, List, ListItem, ListItemText, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import api from '../api/client'

interface Overview {
  status_counts: Record<string, number>
  avg_total_days_by_site: Record<string, number>
  aging_over_30: number
  aging_over_45: number
  capital_binding_by_site: Record<string, number>
}

interface Slowest {
  machine_number: string
  refurb_site: string
  status: string
  days_in_current_status: number
}

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [slowest, setSlowest] = useState<Slowest[]>([])

  useEffect(() => {
    const load = async () => {
      const [o, s] = await Promise.all([api.get<Overview>('/dashboard/overview'), api.get<Slowest[]>('/dashboard/slowest')])
      setOverview(o.data)
      setSlowest(s.data)
    }
    void load()
  }, [])

  if (!overview) return <Typography>Lade Dashboard...</Typography>

  return (
    <Grid2 container spacing={2}>
      <Grid2 size={6}>
        <Card><CardContent>
          <Typography variant="h6">Pipeline Counts je Status</Typography>
          <List dense>
            {Object.entries(overview.status_counts).map(([k, v]) => <ListItem key={k}><ListItemText primary={`${k}: ${v}`} /></ListItem>)}
          </List>
        </CardContent></Card>
      </Grid2>
      <Grid2 size={6}>
        <Card><CardContent>
          <Typography variant="h6">Aging</Typography>
          <Typography>&gt;30 Tage: {overview.aging_over_30}</Typography>
          <Typography>&gt;45 Tage: {overview.aging_over_45}</Typography>
        </CardContent></Card>
      </Grid2>
      <Grid2 size={6}>
        <Card><CardContent>
          <Typography variant="h6">Ø Durchlaufzeit je Standort</Typography>
          {Object.entries(overview.avg_total_days_by_site).map(([site, value]) => (
            <Typography key={site}>{site}: {value} Tage</Typography>
          ))}
        </CardContent></Card>
      </Grid2>
      <Grid2 size={6}>
        <Card><CardContent>
          <Typography variant="h6">Kapitalbindung je Standort</Typography>
          {Object.entries(overview.capital_binding_by_site).map(([site, value]) => (
            <Typography key={site}>{site}: € {Number(value).toFixed(2)}</Typography>
          ))}
        </CardContent></Card>
      </Grid2>
      <Grid2 size={12}>
        <Card><CardContent>
          <Typography variant="h6">Top 10 langsamste Maschinen</Typography>
          <List dense>
            {slowest.map((m) => (
              <ListItem key={m.machine_number}><ListItemText primary={`${m.machine_number} | ${m.refurb_site} | ${m.status}`} secondary={`${m.days_in_current_status} Tage im Status`} /></ListItem>
            ))}
          </List>
        </CardContent></Card>
      </Grid2>
    </Grid2>
  )
}
