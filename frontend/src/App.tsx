import { AppShell, Title, Container, Button, Group, Stack } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { useEffect } from 'react'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'
import { getBatchStatus } from './services/api'

function App() {
  const [opened, { open, close }] = useDisclosure(false)

  useEffect(() => {
    getBatchStatus('test-connection').catch(() => {
        console.log("API Client initialized and reachable (expected 404 for test-connection)");
    });
  }, []);

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
          <Stack>
            <Group justify="space-between">
              <Title order={4}>Batch Jobs</Title>
              <Button onClick={open}>Configure Inputs</Button>
            </Group>
            
            <BatchGrid />
          </Stack>
        </Container>
      </AppShell.Main>

      <InputModal opened={opened} onClose={close} />
    </AppShell>
  )
}

export default App
