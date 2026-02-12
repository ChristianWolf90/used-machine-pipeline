import { Button, Chip, MenuItem, Stack, TextField, Typography } from '@mui/material'
import { DataGrid, GridColDef } from '@mui/x-data-grid'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Machine } from '../types'

const statuses = ['', 'UNDERWAY', 'INTAKE_ASSESSMENT', 'REFURBISHMENT', 'SALE_READY']
const sites = ['', 'Passau', 'Andernach', 'Welzow']

export default function MachineListPage() {
  const navigate = useNavigate()
  const [machines, setMachines] = useState<Machine[]>([])
  const [site, setSite] = useState('')
  const [status, setStatus] = useState('')
  const [olderThan, setOlderThan] = useState('')

  const fetchMachines = async () => {
    const { data } = await api.get<Machine[]>('/machines', { params: { site, status, older_than_days: olderThan || undefined } })
    setMachines(data)
  }

  useEffect(() => { void fetchMachines() }, [])

  const cols: GridColDef[] = [
    { field: 'machine_number', headerName: 'Maschine', flex: 1 },
    { field: 'refurb_site', headerName: 'Standort', flex: 1 },
    { field: 'status', headerName: 'Status', flex: 1, renderCell: (p) => <Chip label={p.value} size="small" /> },
    { field: 'dt_rental_exit', headerName: 'Rental Exit', flex: 1 },
  ]

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Maschinenliste</Typography>
      <Stack direction="row" spacing={2}>
        <TextField select label="Standort" value={site} onChange={(e) => setSite(e.target.value)} sx={{ minWidth: 180 }}>
          {sites.map((s) => <MenuItem key={s} value={s}>{s || 'Alle'}</MenuItem>)}
        </TextField>
        <TextField select label="Status" value={status} onChange={(e) => setStatus(e.target.value)} sx={{ minWidth: 220 }}>
          {statuses.map((s) => <MenuItem key={s} value={s}>{s || 'Alle'}</MenuItem>)}
        </TextField>
        <TextField label="> Tage im Status" value={olderThan} onChange={(e) => setOlderThan(e.target.value)} />
        <Button variant="contained" onClick={fetchMachines}>Filter anwenden</Button>
      </Stack>
      <div style={{ height: 500 }}>
        <DataGrid
          rows={machines}
          getRowId={(r) => r.id}
          columns={cols}
          onRowClick={(row) => navigate(`/machines/${row.id}`)}
        />
      </div>
    </Stack>
  )
}
