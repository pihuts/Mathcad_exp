import { Modal, NumberInput, Button, Stack, Group, Tabs, FileInput, Text, Select, SegmentedControl, TextInput, Textarea } from '@mantine/core'
import { useState, useEffect } from 'react'
import { generateRange } from '../utils/generators'
import { parseCSV, getHeaders } from '../utils/csv_parser'
import type { InputConfig } from '../services/api'

const UNIT_PRESETS = [
  { value: "", label: "Unitless (no units)" },
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
  const [inputType, setInputType] = useState<'number' | 'string'>('number')

  // Range state
  const [start, setStart] = useState<number | string>(0)
  const [end, setEnd] = useState<number | string>(10)
  const [step, setStep] = useState<number | string>(1)

  // String state
  const [stringValue, setStringValue] = useState<string>('')
  const [listValues, setListValues] = useState<string>('')

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

  // Reset activeTab when inputType changes
  useEffect(() => {
    if (inputType === 'string') {
      setActiveTab('list');
    } else if (inputType === 'number') {
      setActiveTab('range');
    }
  }, [inputType]);

  const handleSave = () => {
    let value: any = null;

    if (inputType === 'number') {
      // Numeric input handling
      if (activeTab === 'range') {
        value = generateRange(Number(start), Number(end), Number(step));
      } else if (activeTab === 'csv' && selectedHeader && csvData.length > 0) {
        value = csvData.map(row => Number(row[selectedHeader]));
      }
    } else if (inputType === 'string') {
      // String input handling
      if (activeTab === 'single') {
        const trimmed = stringValue.trim();
        if (trimmed === '') return; // Don't save empty strings
        value = [trimmed];
      } else if (activeTab === 'list') {
        const rawValues = listValues
          .split(/\r?\n/)
          .map(v => v.trim())
          .filter(v => v.length > 0);
        value = [...new Set(rawValues)];
        if (value.length === 0) return;
      } else if (activeTab === 'csv' && selectedHeader && csvData.length > 0) {
        const rawCsvValues = csvData
          .map(row => String(row[selectedHeader]).trim())
          .filter(v => v.length > 0);
        value = [...new Set(rawCsvValues)];
        if (value.length === 0) return;
      }
    }

    if (value !== null) {
      onSave({
        alias: alias,
        value: value,
        units: inputType === 'number' ? (selectedUnits || undefined) : undefined
      });
    }
  }

  return (
    <Modal opened={opened} onClose={onClose} title={`Configure Alias: ${alias}`} size="md" centered>
      <Stack gap="md" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
        <SegmentedControl
          value={inputType}
          onChange={(val) => setInputType(val as 'number' | 'string')}
          data={[
            { label: 'Number', value: 'number' },
            { label: 'String', value: 'string' }
          ]}
          fullWidth
        />

        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tabs.List>
            {inputType === 'number' && <Tabs.Tab value="range">Range</Tabs.Tab>}
            {inputType === 'string' && <Tabs.Tab value="single">Single Value</Tabs.Tab>}
            {inputType === 'string' && <Tabs.Tab value="list">List</Tabs.Tab>}
            <Tabs.Tab value="csv">CSV File</Tabs.Tab>
          </Tabs.List>

          {inputType === 'number' && (
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
          )}

          {inputType === 'string' && (
            <Tabs.Panel value="single" pt="md">
              <Stack>
                <TextInput
                  label="String Value"
                  placeholder="Enter text value (e.g., material name, label)"
                  value={stringValue}
                  onChange={(e) => setStringValue(e.currentTarget.value)}
                />
                <Text size="xs" c="dimmed">
                  This value will be passed as-is to MathcadPy's set_string_input
                </Text>
              </Stack>
            </Tabs.Panel>
          )}

          {inputType === 'string' && (
            <Tabs.Panel value="list" pt="md">
              <Stack>
                <Textarea
                  label="String Values (one per line)"
                  placeholder={"Material A\nMaterial B\nMaterial C"}
                  value={listValues}
                  onChange={(e) => setListValues(e.currentTarget.value)}
                  autosize
                  minRows={3}
                  maxRows={10}
                  description="Enter one value per line. Empty lines and duplicates are removed automatically."
                />
                {listValues.trim().length > 0 && (
                  <Text size="xs" c="dimmed">
                    {[...new Set(listValues.split(/\r?\n/).map(v => v.trim()).filter(v => v.length > 0))].length} unique value(s)
                  </Text>
                )}
              </Stack>
            </Tabs.Panel>
          )}

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

        {inputType === 'number' && (
          <Select
            label="Units"
            placeholder="Select units (optional)"
            data={UNIT_PRESETS}
            value={selectedUnits}
            onChange={setSelectedUnits}
            searchable
            allowDeselect={false}
          />
        )}

        <Group justify="flex-end" mt="md">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave}>Save Configuration</Button>
        </Group>
      </Stack>
    </Modal>
  )
}
