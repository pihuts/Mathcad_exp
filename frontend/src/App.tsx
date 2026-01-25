import { AppShell, Title, Container, Button, Group, Stack } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { BatchGrid } from './components/BatchGrid'
import { InputModal } from './components/InputModal'

function App() {
  const [opened, { open, close }] = useDisclosure(false)

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
