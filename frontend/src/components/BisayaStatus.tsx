import { Text, Transition, Group, Loader } from '@mantine/core';
import { useEffect, useState } from 'react';

const PHRASES = [
    "Gahulat pa ko...",
    "Ayaw pagdali, nag-work pa ko...",
    "Hapit na jud guys...",
    "Inom sa'g tubig...",
    "Bug-at ni da...",
    "Relax lang, kaya ra ni...",
    "Nag-huna-huna pa ang computer...",
    "Pahulay sa kadiyot...",
    "Padayon lang...",
    "Gamay na lang kulang..."
];

interface BisayaStatusProps {
    status: string; // 'running', 'completed', 'stopped', etc.
}

export function BisayaStatus({ status }: BisayaStatusProps) {
    const [index, setIndex] = useState(0);
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        if (status !== 'running') {
            return;
        }

        const interval = setInterval(() => {
            setVisible(false);
            setTimeout(() => {
                setIndex((prev) => (prev + 1) % PHRASES.length);
                setVisible(true);
            }, 500); // Wait for fade out
        }, 4000); // Change every 4 seconds

        return () => clearInterval(interval);
    }, [status]);

    if (status !== 'running') return null;

    return (
        <Group gap="xs" mt="xs" justify="center">
            <Loader size="xs" color="blue" type="dots" />
            <Transition mounted={visible} transition="fade" duration={400} timingFunction="ease">
                {(styles) => (
                    <Text size="sm" c="dimmed" fs="italic" style={styles}>
                        {PHRASES[index]}
                    </Text>
                )}
            </Transition>
        </Group>
    );
}
