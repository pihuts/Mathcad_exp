import { Modal, NumberInput, Button, Stack, Group } from '@mantine/core'

interface InputModalProps {
  opened: boolean
  onClose: () => void
}

export const InputModal = ({ opened, onClose }: InputModalProps) => {
  return (
    <Modal opened={opened} onClose={onClose} title="Configure Batch Inputs">
      <Stack>
        <NumberInput
          label="Range Start"
          placeholder="0"
        />
        <NumberInput
          label="Range End"
          placeholder="100"
        />
        <NumberInput
          label="Increment"
          placeholder="10"
        />
        <Group justify="flex-end" mt="md">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={onClose}>Save Configuration</Button>
        </Group>
      </Stack>
    </Modal>
  )
}
