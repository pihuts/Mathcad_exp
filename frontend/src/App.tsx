import { AppShell, Title, Container, Button, Group, Stack, Progress, Text, TextInput, Table, Badge, ActionIcon } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconSettings } from '@tabler/icons-react'
import { useState, useMemo } from 'react'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'
import { useBatch } from './hooks/useBatch'
import { getInputs } from './services/api'
import { generateCartesian } from './utils/generators'

function App() {
  const [opened, { open, close }] = useDisclosure(false)
  const [filePath, setFilePath] = useState('D:\\Mathcad_exp\\test_files\\simple.mcdx')
  const [aliases, setAliases] = useState<{ alias: string, name: string }[]>([])
  const [aliasConfigs, setAliasConfigs] = useState<Record<string, any[]>>({})
  const [selectedAlias, setSelectedAlias] = useState<string | null>(null)
  
  const { startBatch, batchData, currentBatchId, stopBatch } = useBatch()

  const progress = batchData ? (batchData.total > 0 ? (batchData.completed / batchData.total) * 100 : 0) : 0;

  const handleAnalyze = async () => {
    try {
      const meta = await getInputs(filePath);
      setAliases(meta.inputs);
      // Reset configs if aliases changed significantly or just keep them
    } catch (err) {
      console.error("Failed to analyze file", err);
    }
  }

  const handleConfigureAlias = (alias: string) => {
    setSelectedAlias(alias);
    open();
  }

  const handleSaveAliasConfig = (alias: string, values: any[]) => {
    setAliasConfigs(prev => ({ ...prev, [alias]: values }));
    close();
  }

  const iterationCount = useMemo(() => {
    const keys = Object.keys(aliasConfigs);
    if (keys.length === 0) return 0;
    return keys.reduce((acc, key) => acc * aliasConfigs[key].length, 1);
  }, [aliasConfigs]);

  const handleRun = () => {
    // Check if all aliases have configs or use default? 
    // For now, only use configured ones.
    if (Object.keys(aliasConfigs).length === 0) return;

    const combinations = generateCartesian(aliasConfigs);
    const inputs = combinations.map(combo => ({
      ...combo,
      path: filePath
    }));
    
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
          <Stack gap="xl">
            <Group align="flex-end">
              <TextInput 
                label="Mathcad File Path"
                placeholder="C:\path\to\file.mcdx"
                value={filePath}
                onChange={(e) => setFilePath(e.currentTarget.value)}
                style={{ flex: 1 }}
              />
              <Button onClick={handleAnalyze}>Analyze File</Button>
            </Group>

            {aliases.length > 0 && (
              <Stack gap="xs">
                <Title order={5}>Input Aliases</Title>
                <Table>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Alias</Table.Th>
                      <Table.Th>Name</Table.Th>
                      <Table.Th>Configuration</Table.Th>
                      <Table.Th style={{ width: 100 }}>Action</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {aliases.map((a) => (
                      <Table.Tr key={a.alias}>
                        <Table.Td>{a.alias}</Table.Td>
                        <Table.Td>{a.name}</Table.Td>
                        <Table.Td>
                          {aliasConfigs[a.alias] ? (
                            <Badge color="blue" variant="light">
                              {aliasConfigs[a.alias].length} values
                            </Badge>
                          ) : (
                            <Badge color="gray" variant="dot">Single Value (Default)</Badge>
                          )}
                        </Table.Td>
                        <Table.Td>
                          <ActionIcon variant="light" onClick={() => handleConfigureAlias(a.alias)}>
                            <IconSettings size={18} />
                          </ActionIcon>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
                
                <Group justify="space-between" mt="md">
                  <Text size="sm" fw={500}>
                    Total Iterations: {iterationCount}
                  </Text>
                  <Button 
                    disabled={iterationCount === 0} 
                    onClick={handleRun}
                    loading={batchData?.status === 'running'}
                  >
                    Run Batch
                  </Button>
                </Group>
              </Stack>
            )}

            {batchData && (
              <Stack gap="xs">
                <Group justify="space-between">
                  <Title order={4}>Batch Progress</Title>
                  <Group>
                    <Text size="sm">Progress: {batchData.completed} / {batchData.total}</Text>
                    {batchData.status === 'running' && (
                      <Button color="red" variant="light" size="xs" onClick={() => stopBatch(currentBatchId!)}>Stop Batch</Button>
                    )}
                  </Group>
                </Group>
                <Progress value={progress} animated={batchData.status === 'running'} />
                <BatchGrid data={batchData?.results} />
              </Stack>
            )}
          </Stack>
        </Container>
      </AppShell.Main>

      <InputModal 
        opened={opened} 
        onClose={close} 
        alias={selectedAlias || ''}
        onSave={(values) => handleSaveAliasConfig(selectedAlias!, values)} 
      />
    </AppShell>
  )
}

export default App
