import { AppShell, Title, Container } from '@mantine/core'

function App() {
  return (
    <AppShell
      header={{ height: 60 }}
      padding="md"
    >
      <AppShell.Header p="md">
        <Title order={3}>Mathcad Automator - Batch Processor</Title>
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl">
          {/* Grid and other components will go here */}
          <p>Welcome to the Batch Processing System.</p>
        </Container>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
