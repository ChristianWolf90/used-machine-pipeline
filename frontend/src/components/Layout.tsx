import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material'
import { Link, Outlet, useNavigate } from 'react-router-dom'
import { clearSession, getSession } from '../auth/auth'

export default function Layout() {
  const navigate = useNavigate()
  const session = getSession()

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Used Machine Pipeline</Typography>
          <Button color="inherit" component={Link} to="/machines">Machines</Button>
          <Button color="inherit" component={Link} to="/dashboard">Dashboard</Button>
          <Button
            color="inherit"
            onClick={() => {
              clearSession()
              navigate('/login')
            }}
          >
            Logout ({session?.role})
          </Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 3 }}>
        <Outlet />
      </Container>
    </>
  )
}
