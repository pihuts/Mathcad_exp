import { Modal, NumberInput, Button, Stack, Group, Tabs, FileInput, Text, Select } from '@mantine/core'
import { useState, useEffect } from 'react'
import { generateRange } from '../utils/generators'
import { parseCSV, getHeaders } from '../utils/csv_parser'
import type { InputConfig } from '../services/api'

const UNIT_PRESETS = [
  { value: "", label: "Use Worksheet Units (Default)" },
  { value: "in", label: "in (inches)" },
  { value: "ft", label: "ft (feet)" },
  { value: "mm", label: "mm (millimeters)" },
  { value: "m", label: "m (meters)" },
  { value: "kip", label: "kip (kilopound force)" },
  { value: "lbf", label: "lbf (pound force)" },
  { value: "N", label: "N (newton)" },
  { value: "kN", label: "kN (kilonewton)" },
  { value: "Pa", label: "Pa (pascal)" },
  { value: "MPa", label: "MPa (megapascal)" },
  { value: "psi", label: "psi (pounds per square inch)" },
  { value: "ksf", label: "ksf (kip per square foot)" },
  { value: "kip/ft", label: "kip/ft (force per length)" },
  { value: "kip-in", label: "kip-in (moment)" },
  { value: "lb-ft", label: "lb-ft (pound-foot moment)" },
];

interface InputModalProps {
  opened: boolean
  onClose: () => void
  alias: string
  onSave: (config: InputConfig) => void  // Changed from (values: any[]) => void
}

export const InputModal = ({ opened, onClose, alias, onSave }: InputModalProps) => {
  const [activeTab, setActiveTab] = useState<string | null>('range')
  
  // Range state
  const [start, setStart] = useState<number | string>(0)
  const [end, setEnd] = useState<number | string>(10)
  const [step, setStep] = useState<number | string>(1)
  
  // CSV state
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvHeaders, setCsvHeaders] = useState<string[]>([])
  const [selectedHeader, setSelectedHeader] = useState<string | null>(null)
  const [csvData, setCsvData] = useState<any[]>([])
  const [selectedUnits, setSelectedUnits] = useState<string | null>("")

  useEffect(() => {
    if (csvFile) {
      getHeaders(csvFile).then(setCsvHeaders).catch(console.error);
      parseCSV(csvFile).then(setCsvData).catch(console.error);
    } else {
      setCsvHeaders([]);
      setCsvData([]);
      setSelectedHeader(null);
    }
  }, [csvFile]);

  const handleSave = () => {
    const value: any = activeTab === 'range'
      ? generateRange(Number(start), Number(end), Number(step))
      : (selectedHeader && csvData.length > 0
        ? csvData.map(row => row[selectedHeader])
        : null);

    if (value !== null) {
      onSave({
        alias: alias,
        value: value,
        units: selectedUnits || undefined  // Convert "" to undefined
      });
    }
  }

  return (
    <Modal opened={opened} onClose={onClose} title={`Configure Alias: ${alias}`} size="lg">
      <Stack>
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tabs.List>
            <Tabs.Tab value="range">Range</Tabs.Tab>
            <Tabs.Tab value="csv">CSV File</Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="range" pt="md">
            <Stack>
              <Group grow>
                <NumberInput label="Start" value={start} onChange={setStart} />
                <NumberInput label="End" value={end} onChange={setEnd} />
              </Group>
              <NumberInput label="Step" value={step} onChange={setStep} />
              <Text size="xs" c="dimmed">
                Resulting values: {generateRange(Number(start), Number(end), Number(step)).join(', ')}
              </Text>
            </Stack>
          </Tabs.Panel>

          <Tabs.Panel value="csv" pt="md">
            <Stack>
              <FileInput 
                label="Upload CSV" 
                placeholder="Choose file" 
                value={csvFile} 
                onChange={setCsvFile}
                accept=".csv"
              />
              {csvHeaders.length > 0 && (
                <Select
                  label="Select Column"
                  placeholder="Choose column"
                  data={csvHeaders}
                  value={selectedHeader}
                  onChange={setSelectedHeader}
                />
              )}
              {selectedHeader && (
                <Text size="xs" c="dimmed">
                  Found {csvData.length} rows.
                </Text>
              )}
            </Stack>
          </Tabs.Panel>
        </Tabs>

        <Select
          label="Units"
          placeholder="Select units (optional)"
          data={UNIT_PRESETS}
          value={selectedUnits}
          onChange={setSelectedUnits}
          searchable
          clearable  // Allow clearing selection (goes back to default "")
        />

        <Group justify="flex-end" mt="md">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave}>Save Configuration</Button>
        </Group>
      </Stack>
    </Modal>
  )
}
