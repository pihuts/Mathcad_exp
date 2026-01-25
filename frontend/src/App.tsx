import { AppShell, Title, Container, Button, Group, Stack, Progress, Text } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'
import { useBatch } from './hooks/useBatch'

function App() {
  const [opened, { open, close }] = useDisclosure(false)
  const { startBatch, batchData, currentBatchId, stopBatch } = useBatch()

  const progress = batchData ? (batchData.total > 0 ? (batchData.completed / batchData.total) * 100 : 0) : 0;

  const handleRun = (config: { start: number, end: number, step: number, path: string, alias: string }) => {
    const inputs = [];
    // Generate simple range batch
    for (let v = config.start; v <= config.end; v += config.step) {
      inputs.push({ [config.alias]: v, "path": config.path });
    }
    
    startBatch({
      batch_id: `batch-${Date.now()}`,
      inputs,
      output_dir: "D:\\Mathcad_exp\\results"
    });
  }

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

      <InputModal opened={opened} onClose={close} onRun={handleRun} />
    </AppShell>
  )
}

export default App
