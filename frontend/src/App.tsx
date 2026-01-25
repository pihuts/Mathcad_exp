import { AppShell, Title, Container, Button, Group, Stack, Progress, Text } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'
import { useBatch } from './hooks/useBatch'

function App() {
  const [opened, { open, close }] = useDisclosure(false)
  const { batchData, currentBatchId, stopBatch } = useBatch()

  const progress = batchData ? (batchData.completed / batchData.total) * 100 : 0;

  return (
    <AppShell
      header={{ height: 60 }}
      padding="md"
    >
      <AppShell.Header p="md">
        <Group justify="space-between" h="100%">
          <Title order={3}>Mathcad Automator - Batch Processor</Title>
          {currentBatchId && (
            <Text size="sm" c="dimmed">Active Batch: {currentBatchId}</Text>
          )}
        </Group>
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl">
          <Stack>
            {batchData && (
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm">Progress: {batchData.completed} / {batchData.total}</Text>
                  {batchData.status === 'running' && (
                    <Button color="red" variant="light" size="xs" onClick={() => stopBatch(currentBatchId!)}>Stop Batch</Button>
                  )}
                </Group>
                <Progress value={progress} animated={batchData.status === 'running'} />
              </Stack>
            )}

            <Group justify="space-between">
              <Title order={4}>Batch Results</Title>
              <Button onClick={open}>Configure & Run</Button>
            </Group>
            
            <BatchGrid data={batchData?.results} />
          </Stack>
        </Container>
      </AppShell.Main>

      <InputModal opened={opened} onClose={close} />
    </AppShell>
  )
}

export default App
