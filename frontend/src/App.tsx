import { AppShell, Title, Container, Button, Group, Stack, Progress, Text, TextInput, Table, Badge, ActionIcon, Alert, Tabs, Paper } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconSettings, IconAlertCircle } from '@tabler/icons-react'
import { useState, useMemo } from 'react'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'
import { WorkflowBuilder } from './components/WorkflowBuilder'
import { MappingModal } from './components/MappingModal'
import { useBatch } from './hooks/useBatch'
import { useWorkflow } from './hooks/useWorkflow'
import { getInputs } from './services/api'
import { generateCartesian } from './utils/generators'
import type { WorkflowFile, FileMapping, MetaData, WorkflowConfig, InputConfig } from './services/api'
import { WorkflowStatus } from './services/api'

function App() {
  const [opened, { open, close }] = useDisclosure(false)
  const [filePath, setFilePath] = useState('')
  const [aliases, setAliases] = useState<{ alias: string, name: string }[]>([])
  const [aliasConfigs, setAliasConfigs] = useState<Record<string, any[]>>({})
  const [aliasUnits, setAliasUnits] = useState<Record<string, string>>({})
  const [selectedAlias, setSelectedAlias] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Workflow state
  const [activeTab, setActiveTab] = useState<string | null>('batch');
  const [workflowFiles, setWorkflowFiles] = useState<WorkflowFile[]>([]);
  const [workflowMappings, setWorkflowMappings] = useState<FileMapping[]>([]);
  const [mappingModalFile, setMappingModalFile] = useState<WorkflowFile | null>(null);
  const [workflowInputFile, setWorkflowInputFile] = useState<WorkflowFile | null>(null);
  const [filesMetadata, setFilesMetadata] = useState<Record<string, MetaData>>({});
  const [workflowError, setWorkflowError] = useState<string | null>(null);

  const { startBatch, batchData, currentBatchId, stopBatch } = useBatch()

  const {
    createWorkflow,
    stopWorkflow,
    workflowData,
    activeWorkflowId,
    isLoading: workflowLoading,
    isCreating,
    isStopping,
  } = useWorkflow();

  const progress = batchData ? (batchData.total > 0 ? (batchData.completed / batchData.total) * 100 : 0) : 0;

  // Workflow handler functions
  const handleOpenMappingModal = (file: WorkflowFile) => {
    setMappingModalFile(file);
  };

  const handleSaveMappings = (mappings: FileMapping[]) => {
    if (mappingModalFile) {
      // Remove old mappings for this file and add new ones
      const otherMappings = workflowMappings.filter(
        (m) => m.target_file !== mappingModalFile.file_path
      );
      setWorkflowMappings([...otherMappings, ...mappings]);
    }
    setMappingModalFile(null);
  };

  const handleConfigureWorkflowInputs = async (file: WorkflowFile) => {
    if (!file.file_path) return;

    try {
      const meta = await getInputs(file.file_path);
      setFilesMetadata(prev => ({
        ...prev,
        [file.file_path]: meta,
      }));
      setWorkflowInputFile(file);
    } catch (err: any) {
      console.error("Failed to analyze file", err);
    }
  };

  const handleSaveWorkflowInputs = (alias: string, config: any) => {
    // Handle InputConfig object {alias, value, units} from InputModal
    const values = Array.isArray(config) ? config : config.value;
    const units = Array.isArray(config) ? undefined : config.units;

    if (workflowInputFile) {
      const newFiles = [...workflowFiles];
      const fileIndex = newFiles.findIndex(f => f.file_path === workflowInputFile.file_path);

      if (fileIndex >= 0) {
        // Create InputConfig for the alias
        const inputConfig: InputConfig = {
          alias,
          value: Array.isArray(values) ? values[0] : values,
          units,
        };

        // Replace or add input config for this alias
        const existingIndex = newFiles[fileIndex].inputs.findIndex(i => i.alias === alias);
        if (existingIndex >= 0) {
          newFiles[fileIndex].inputs[existingIndex] = inputConfig;
        } else {
          newFiles[fileIndex].inputs.push(inputConfig);
        }

        setWorkflowFiles(newFiles);
      }
    }

    setWorkflowInputFile(null);
  };

  const handleRunWorkflow = () => {
    if (workflowFiles.length === 0) return;

    const workflowConfig: WorkflowConfig = {
      name: `workflow-${Date.now()}`,
      files: workflowFiles,
      mappings: workflowMappings,
      stop_on_error: true,
    };

    createWorkflow(workflowConfig);
  };

  const workflowProgress = workflowData ? workflowData.progress : 0;

  const handleAnalyze = async () => {
    setError(null);
    setIsAnalyzing(true);
    try {
      const meta = await getInputs(filePath);
      setAliases(meta.inputs);
      // Reset configs if aliases changed significantly or just keep them
    } catch (err: any) {
      console.error("Failed to analyze file", err);
      // Try to extract useful message
      const msg = err.response?.data?.detail || err.message || "Failed to analyze file";
      setError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  }


  const handleConfigureAlias = (alias: string) => {
    setSelectedAlias(alias);
    open();
  }

  const handleSaveAliasConfig = (alias: string, config: any) => {
    // Handle InputConfig object {alias, value, units} from InputModal
    const values = Array.isArray(config) ? config : config.value;
    const units = Array.isArray(config) ? undefined : config.units;

    setAliasConfigs(prev => ({ ...prev, [alias]: values }));
    if (units) {
      setAliasUnits(prev => ({ ...prev, [alias]: units }));
    }
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
    const inputs = combinations.map(combo => {
      // Add units to each input value
      const inputWithUnits: Record<string, any> = { path: filePath };
      for (const [key, value] of Object.entries(combo)) {
        const units = aliasUnits[key];
        if (units) {
          inputWithUnits[key] = { value, units };
        } else {
          inputWithUnits[key] = value;
        }
      }
      return inputWithUnits;
    });

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
          <Tabs value={activeTab} onChange={setActiveTab}>
            <Tabs.List>
              <Tabs.Tab value="batch">Batch Processing</Tabs.Tab>
              <Tabs.Tab value="workflow">Workflow Orchestration</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="batch">
              <Stack gap="xl">
                {error && (
                  <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" withCloseButton onClose={() => setError(null)}>
                    {error}
                  </Alert>
                )}
                <Group align="flex-end">
                  <TextInput
                    label="Mathcad File Path"
                    placeholder="C:\path\to\file.mcdx"
                    value={filePath}
                    onChange={(e) => setFilePath(e.currentTarget.value)}
                    style={{ flex: 1 }}
                  />
                  <Button
                    onClick={handleAnalyze}
                    loading={isAnalyzing}
                    disabled={isAnalyzing || !filePath}
                  >
                    Analyze File
                  </Button>
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
            </Tabs.Panel>

            <Tabs.Panel value="workflow">
              <Stack gap="xl">
                <Title order={3}>Workflow Orchestration</Title>
                <Text size="sm" c="dimmed">
                  Chain multiple Mathcad files where outputs drive downstream inputs. Files execute in order (top to bottom).
                </Text>

                {workflowError && (
                  <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" withCloseButton onClose={() => setWorkflowError(null)}>
                    {workflowError}
                  </Alert>
                )}

                <WorkflowBuilder
                  files={workflowFiles}
                  mappings={workflowMappings}
                  onFilesChange={setWorkflowFiles}
                  onMappingsChange={setWorkflowMappings}
                  onOpenMappingModal={handleOpenMappingModal}
                  onConfigureInputs={handleConfigureWorkflowInputs}
                />

                <Group justify="flex-end">
                  <Button
                    disabled={workflowFiles.length === 0 || workflowFiles.some(f => !f.file_path)}
                    onClick={handleRunWorkflow}
                    loading={isCreating || (!!activeWorkflowId && workflowLoading)}
                  >
                    Run Workflow
                  </Button>
                </Group>

                {activeWorkflowId && (
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Title order={4}>Workflow Progress</Title>
                      <Group>
                        <Text size="sm">
                          Status: {workflowData?.status?.toUpperCase() || 'RUNNING'}
                        </Text>
                        {workflowData?.status === WorkflowStatus.RUNNING && (
                          <Button color="red" variant="light" size="xs" onClick={stopWorkflow} loading={isStopping}>
                            Stop Workflow
                          </Button>
                        )}
                      </Group>
                    </Group>
                    <Progress value={workflowProgress} animated={workflowData?.status === WorkflowStatus.RUNNING} />

                    {workflowData && (
                      <Stack gap="xs" mt="md">
                        <Group>
                          <Text size="sm">Current File: {workflowData.current_file_index + 1} / {workflowData.total_files}</Text>
                          <Text size="sm">Completed: {workflowData.completed_files.length}</Text>
                        </Group>

                        {workflowData.completed_files.length > 0 && (
                          <Paper p="md" withBorder>
                            <Text fw={500} mb="xs">Completed Files:</Text>
                            <Stack gap="xs">
                              {workflowData.completed_files.map((file, idx) => (
                                <Text key={idx} size="sm">{idx + 1}. {file}</Text>
                              ))}
                            </Stack>
                          </Paper>
                        )}

                        {workflowData.status === WorkflowStatus.FAILED && workflowData.error && (
                          <Alert color="red">
                            <Text size="sm">Error: {workflowData.error}</Text>
                          </Alert>
                        )}
                      </Stack>
                    )}
                  </Stack>
                )}
              </Stack>
            </Tabs.Panel>
          </Tabs>
        </Container>
      </AppShell.Main>
    </AppShell>

    {/* Modals must be outside AppShell for proper overlay rendering */}
    <InputModal
      opened={opened}
      onClose={close}
      alias={selectedAlias || ''}
      onSave={(values) => handleSaveAliasConfig(selectedAlias!, values)}
    />

    <MappingModal
      opened={!!mappingModalFile}
      onClose={() => setMappingModalFile(null)}
      targetFile={mappingModalFile || { file_path: '', inputs: [], position: 0 }}
      allFiles={workflowFiles}
      filesMetadata={filesMetadata}
      currentMappings={workflowMappings.filter(m => m.target_file === mappingModalFile?.file_path)}
      onSave={handleSaveMappings}
    />

    <InputModal
      opened={!!workflowInputFile}
      onClose={() => setWorkflowInputFile(null)}
      alias={workflowInputFile?.inputs[0]?.alias || ''}
      onSave={(values) => handleSaveWorkflowInputs(workflowInputFile?.inputs[0]?.alias || '', values)}
    />
  )
}

export default App
