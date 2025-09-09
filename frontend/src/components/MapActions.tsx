type MapActionsProps = {
  onClear: () => void;
  endpoint: string;
  result: number | null;
  loading: boolean;
  onRequest: () => void;
};

export function MapActions({
  onClear,
  result,
  loading,
  onRequest,
}: MapActionsProps) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateRows: 'auto auto auto auto',
        gap: '16px',
        alignItems: 'center',
        justifyItems: 'end',
        minWidth: 160,
      }}
    >
      <button
        onClick={onClear}
        style={{
          padding: '10px 20px',
          background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 16,
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(118,75,162,0.15)',
          width: '100%',
        }}
      >
        Clear All Markers
      </button>
      <button
        onClick={onRequest}
        disabled={loading}
        style={{
          padding: '10px 20px',
          background: loading
            ? 'linear-gradient(90deg, #b3b3b3 0%, #cccccc 100%)'
            : 'linear-gradient(90deg, #43cea2 0%, #185a9d 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 16,
          cursor: loading ? 'not-allowed' : 'pointer',
          boxShadow: '0 2px 8px rgba(67,206,162,0.15)',
          width: '100%',
        }}
      >
        {loading ? 'Loading...' : 'Send Request'}
      </button>
      <div
        style={{
          minWidth: 120,
          minHeight: 40,
          background: '#fff',
          borderRadius: 6,
          boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 24,
          fontWeight: 700,
          color: result === null ? '#aaa' : result === -1 ? '#e53e3e' : '#185a9d',
          border: result === -1 ? '2px solid #e53e3e' : '2px solid #185a9d',
          transition: 'all 0.2s',
          width: '100%',
        }}
      >
        {result === null
          ? 'Result'
          : result === -1
            ? 'Error'
            : result}
      </div>
    </div>
  );
}