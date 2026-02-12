import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { setSession } from '../auth/auth'
import { LoginResponse } from '../types'

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const { data } = await api.post<LoginResponse>('/auth/login', { username, password })
      setSession({ token: data.access_token, role: data.role, site: data.site })
      navigate('/machines')
    } catch {
      setError('Login fehlgeschlagen')
    }
  }

  return (
    <Box display="flex" justifyContent="center" mt={8}>
      <Card sx={{ width: 420 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>Login</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>Admin oder SiteUser anmelden.</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Stack component="form" spacing={2} onSubmit={onSubmit}>
            <TextField label="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            <TextField type="password" label="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Button type="submit" variant="contained">Einloggen</Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}
