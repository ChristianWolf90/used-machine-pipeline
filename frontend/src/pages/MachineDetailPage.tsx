import { Alert, Button, MenuItem, Stack, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import { Machine } from '../types'

const statuses = ['UNDERWAY', 'INTAKE_ASSESSMENT', 'REFURBISHMENT', 'SALE_READY']

export default function MachineDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [machine, setMachine] = useState<Machine | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      const { data } = await api.get<Machine[]>('/machines')
      setMachine(data.find((m) => m.id === id) || null)
    }
    void load()
  }, [id])

  const update = async () => {
    if (!machine) return
    try {
      await api.put(`/machines/${machine.id}`, machine)
      navigate('/machines')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Update fehlgeschlagen')
    }
  }

  if (!machine) return <Typography>Lade Maschine...</Typography>

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Maschine {machine.machine_number}</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <TextField select label="Status" value={machine.status} onChange={(e) => setMachine({ ...machine, status: e.target.value as any })}>
        {statuses.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
      </TextField>
      <TextField
        type="date"
        label="Ankunft Aufbereitung"
        InputLabelProps={{ shrink: true }}
        value={machine.dt_arrival_refurb || ''}
        onChange={(e) => setMachine({ ...machine, dt_arrival_refurb: e.target.value })}
      />
      <TextField
        type="date"
        label="Werkstatt Start"
        InputLabelProps={{ shrink: true }}
        value={machine.dt_workshop_start || ''}
        onChange={(e) => setMachine({ ...machine, dt_workshop_start: e.target.value })}
      />
      <TextField
        type="date"
        label="Verkaufsbereit"
        InputLabelProps={{ shrink: true }}
        value={machine.dt_sale_ready || ''}
        onChange={(e) => setMachine({ ...machine, dt_sale_ready: e.target.value })}
      />
      <Button variant="contained" onClick={update}>Speichern</Button>
    </Stack>
  )
}
