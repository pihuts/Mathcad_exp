import { AgGridReact } from 'ag-grid-react'
import { useMemo } from 'react'
import type { ColDef } from 'ag-grid-community'
import { Badge } from '@mantine/core'
import type { BatchRow } from '../services/api'

interface BatchGridProps {
  data: BatchRow[] | undefined;
}

const StatusRenderer = (params: any) => {
  const status = params.value;
  let color = 'gray';
  if (status === 'done') color = 'green';
  if (status === 'running') color = 'blue';
  if (status === 'error') color = 'red';
  if (status === 'pending') color = 'yellow';
  
  return <Badge color={color} variant="filled">{status}</Badge>;
}

export const BatchGrid = ({ data }: BatchGridProps) => {
  const columnDefs = useMemo<ColDef[]>(() => {
    const baseCols: ColDef[] = [
      { field: 'row', headerName: 'Row', width: 80, pinned: 'left' },
      { field: 'status', headerName: 'Status', width: 120, cellRenderer: StatusRenderer, pinned: 'left' },
    ];

    if (data && data.length > 0) {
      // Find first row that has data to extract columns
      const firstWithData = data.find(r => r.data && Object.keys(r.data).length > 0);
      if (firstWithData && firstWithData.data) {
        const outputKeys = Object.keys(firstWithData.data);
        outputKeys.forEach(key => {
          baseCols.push({
            headerName: key,
            valueGetter: (params) => params.data.data ? params.data.data[key] : '',
            flex: 1,
            minWidth: 100
          });
        });
      }
    }

    baseCols.push({ field: 'error', headerName: 'Error', flex: 2, minWidth: 200 });

    return baseCols;
  }, [data]);

  return (
    <div className="ag-theme-alpine" style={{ height: 600, width: '100%' }}>
      <AgGridReact
        rowData={data || []}
        columnDefs={columnDefs}
        animateRows={true}
      />
    </div>
  )
}
