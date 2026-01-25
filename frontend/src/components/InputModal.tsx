import { Modal, NumberInput, Button, Stack, Group, TextInput } from '@mantine/core'
import { useState } from 'react'

interface InputModalProps {
  opened: boolean
  onClose: () => void
  onRun: (config: { start: number, end: number, step: number, path: string, alias: string }) => void
}

export const InputModal = ({ opened, onClose, onRun }: InputModalProps) => {
  const [start, setStart] = useState<number | string>(0)
  const [end, setEnd] = useState<number | string>(100)
  const [step, setStep] = useState<number | string>(10)
  const [path, setPath] = useState('C:\\temp\\test.mcdx')
  const [alias, setAlias] = useState('L')

  const handleRun = () => {
    onRun({ 
      start: Number(start), 
      end: Number(end), 
      step: Number(step),
      path,
      alias
    });
    onClose();
  }

  return (
    <Modal opened={opened} onClose={onClose} title="Configure Batch Inputs">
      <Stack>
        <TextInput 
          label="Mathcad File Path"
          value={path}
          onChange={(e) => setPath(e.currentTarget.value)}
        />
        <TextInput 
          label="Input Alias"
          value={alias}
          onChange={(e) => setAlias(e.currentTarget.value)}
        />
        <NumberInput
          label="Range Start"
          value={start}
          onChange={setStart}
        />
        <NumberInput
          label="Range End"
          value={end}
          onChange={setEnd}
        />
        <NumberInput
          label="Increment"
          value={step}
          onChange={setStep}
        />
        <Group justify="flex-end" mt="md">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleRun}>Run Batch</Button>
        </Group>
      </Stack>
    </Modal>
  )
}
