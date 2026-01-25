import { AgGridReact } from 'ag-grid-react'
import { useState } from 'react'
import type { ColDef } from 'ag-grid-community'

export const BatchGrid = () => {
  const [columnDefs] = useState<ColDef[]>([
    { field: 'id', headerName: 'ID', width: 100 },
    { field: 'input1', headerName: 'Input 1', flex: 1 },
    { field: 'input2', headerName: 'Input 2', flex: 1 },
    { field: 'status', headerName: 'Status', width: 150 },
  ])

  const [rowData] = useState([
    { id: 1, input1: 'Value A', input2: 'Value B', status: 'Pending' },
    { id: 2, input1: 'Value C', input2: 'Value D', status: 'Running' },
  ])

  return (
    <div className="ag-theme-alpine" style={{ height: 400, width: '100%' }}>
      <AgGridReact
        rowData={rowData}
        columnDefs={columnDefs}
      />
    </div>
  )
}
