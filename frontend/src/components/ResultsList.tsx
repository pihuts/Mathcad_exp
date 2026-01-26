import { Paper, Stack, Text, Group, ActionIcon, Button, ScrollArea, Title } from '@mantine/core';
import { IconFileCheck, IconFolderOpen, IconExternalLink } from '@tabler/icons-react';
import { openFile } from '../services/api';

interface ResultsListProps {
    files: string[];
    outputDir: string;
}

export function ResultsList({ files, outputDir }: ResultsListProps) {
    if (!files || files.length === 0) return null;

    const handleOpenFile = async (path: string) => {
        try {
            await openFile(path);
        } catch (error) {
            console.error('Could not open file', error);
        }
    };

    const handleOpenFolder = async () => {
        try {
            await openFile(outputDir);
        } catch (error) {
            console.error('Could not open folder', error);
        }
    };

    // Show latest first? Or sequential? Sequential (newest at bottom) is standard log, 
    // but for "downloads" usually newest top. Let's do newest on top.
    const reversedFiles = [...files].reverse();

    return (
        <Paper p="md" withBorder mt="md" radius="md" bg="var(--mantine-color-body)">
            <Group justify="space-between" mb="xs">
                <Group gap="xs">
                    <IconFileCheck size={20} color="green" />
                    <Title order={5}>Generated Files ({files.length})</Title>
                </Group>
                <Button
                    variant="light"
                    size="xs"
                    leftSection={<IconFolderOpen size={16} />}
                    onClick={handleOpenFolder}
                >
                    Open Output Folder
                </Button>
            </Group>

            <ScrollArea h={files.length > 5 ? 200 : 'auto'}>
                <Stack gap={8}>
                    {reversedFiles.map((file, idx) => {
                        const fileName = file.split(/[\\/]/).pop();
                        return (
                            <Group key={idx} justify="space-between" p="xs" bg="var(--mantine-color-gray-0)" style={{ borderRadius: 4 }}>
                                <Group gap="xs">
                                    <Text size="sm" c="dimmed" style={{ width: 20 }}>{files.length - idx}.</Text>
                                    <Text size="sm" fw={500} truncate maw={300} title={fileName}>
                                        {fileName}
                                    </Text>
                                </Group>
                                <ActionIcon
                                    variant="subtle"
                                    color="blue"
                                    onClick={() => handleOpenFile(file)}
                                    title="Open File"
                                >
                                    <IconExternalLink size={18} />
                                </ActionIcon>
                            </Group>
                        );
                    })}
                </Stack>
            </ScrollArea>
        </Paper>
    );
}
