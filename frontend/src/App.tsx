import { useState, useEffect } from 'react'
import './App.css'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Asset {
  id: number;
  name: string;
  symbol: string;
  type: string;
  quantity: number;
  current_price: number;
  value_krw: number;
}

interface SearchResult {
  symbol: string;
  name: string;
  type: string;
  exchange: string;
}

interface ApiResponse {
  assets: Asset[];
  total_value_krw: number;
  exchange_rate: number;
  distribution: {
    "원화": number;
    "외화": number;
    "주식": number;
    "비트코인": number;
    "금": number;
  };
  last_updated?: string;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [history, setHistory] = useState<{date: string, total_value_krw: number}[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<{date: string, details: any[]} | null>(null);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchAttempted, setSearchAttempted] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<SearchResult | null>(null);
  const [quantity, setQuantity] = useState('');
  
  // Edit state
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editQuantity, setEditQuantity] = useState('');
  const [waking, setWaking] = useState(false);

  const fetchData = async (retryCount = 0): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/api/assets`);
      if (!response.ok) throw new Error("서버에서 데이터를 가져오지 못했습니다.");
      const result: ApiResponse = await response.json();

      setData(result);
      setError(null);
      setWaking(false);

      const historyRes = await fetch(`${API_BASE}/api/history`);
      if (historyRes.ok) {
        const historyResult = await historyRes.json();
        setHistory(historyResult);
      }
    } catch (error: any) {
      if (retryCount < 4) {
        setWaking(true);
        setTimeout(() => fetchData(retryCount + 1), 15000);
      } else {
        setWaking(false);
        setError("서버 연결에 실패했습니다. 잠시 후 새로고침해 주세요.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(), 60000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async () => {
    if (!searchQuery) return;
    setSearching(true);
    setSearchAttempted(true);
    try {
      const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(searchQuery)}`);
      const result = await response.json();
      setSearchResults(result);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddAsset = async () => {
    if (!selectedAsset || !quantity) return;

    try {
      await fetch(`${API_BASE}/api/assets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedAsset.name,
          symbol: selectedAsset.symbol,
          type: selectedAsset.type,
          quantity: parseFloat(quantity)
        }),
      });
      setSelectedAsset(null);
      setQuantity('');
      setSearchQuery('');
      setSearchResults([]);
      fetchData();
    } catch (error) {
      console.error('Error adding asset:', error);
    }
  };

  const handleUpdateAsset = async (id: number) => {
    if (!editQuantity) return;
    try {
      await fetch(`${API_BASE}/api/assets/${id}?quantity=${parseFloat(editQuantity)}`, {
        method: 'PUT',
      });
      setEditingId(null);
      setEditQuantity('');
      fetchData();
    } catch (error) {
      console.error('Error updating asset:', error);
    }
  };

  const handleDeleteAsset = async (id: number) => {
    try {
      await fetch(`${API_BASE}/api/assets/${id}`, {
        method: 'DELETE',
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting asset:', error);
    }
  };

  const handleCompare = async (date: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/history/${date}`);
      if (!response.ok) throw new Error("Failed to fetch history details");
      const details = await response.json();
      setComparison({ date, details });
      // Scroll to comparison section
      setTimeout(() => {
        document.getElementById('comparison-report')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      console.error('Error comparing history:', error);
      alert("해당 날짜의 상세 기록이 없습니다. (오늘 이후 기록부터 상세 비교가 가능합니다)");
    }
  };

  const pieData = data ? {
    labels: ['원화', '외화', '주식', '비트코인', '금'],
    datasets: [
      {
        data: [
          data.distribution["원화"],
          data.distribution["외화"],
          data.distribution["주식"],
          data.distribution["비트코인"],
          data.distribution["금"],
        ],
        backgroundColor: [
          '#f1c40f',
          '#34495e',
          '#3498db',
          '#e67e22',
          '#f39c12',
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  return (
    <div className="container">
      <header>
        <h1>실시간 자산 트래커</h1>
        {waking && (
          <div className="waking-banner">
            ⏳ 서버 기동 중... 최대 1분 소요됩니다. 자동으로 재시도합니다.
          </div>
        )}
        {error && <div className="error-banner">{error}</div>}
        {data && (
          <div className="dashboard-summary">
            <div className="total-value">
              <h2>총 평가액: {data.total_value_krw.toLocaleString()} KRW</h2>
              <div className="sub-info">
                <p className="exchange-rate">USD/KRW 환율: {data.exchange_rate.toFixed(2)}</p>
                {data.last_updated && <p className="update-time">🕒 마지막 업데이트: {data.last_updated}</p>}
              </div>
            </div>
            {pieData && (
              <div className="pie-chart-container">
                <Pie data={pieData} options={{ maintainAspectRatio: false }} />
              </div>
            )}
          </div>
        )}
      </header>

      <section className="add-asset">
        <h3>자산 검색 및 추가</h3>
        <p className="hint">티커(AAPL, 241180) 또는 영문명(Samsung, TIGER Nikkei)으로 검색해 보세요.</p>
        <div className="search-box">
          <input 
            placeholder="예: Samsung, 241180, TIGER Nikkei, AAPL" 
            value={searchQuery} 
            onChange={e => {
              setSearchQuery(e.target.value);
              setSearchAttempted(false);
            }}
            onKeyPress={e => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={searching}>
            {searching ? '검색 중...' : '검색'}
          </button>
        </div>

        {searchAttempted && searchResults.length === 0 && !searching && (
          <div className="no-results-alert">
            <p>검색 결과가 없습니다. <strong>"{searchQuery}"</strong>를 심볼로 직접 추가하시겠습니까?</p>
            <button className="btn-manual" onClick={() => setSelectedAsset({
              symbol: searchQuery.toUpperCase() === 'KRW' ? 'KRW' : searchQuery,
              name: searchQuery.toUpperCase() === 'KRW' ? '원화 현금' : '직접 입력 자산',
              type: searchQuery.toUpperCase() === 'KRW' ? 'Cash' : 'Manual',
              exchange: 'Internal'
            })}>"{searchQuery}" 심볼로 직접 선택</button>
          </div>
        )}

        <div className="quick-actions">
          <button className="btn-cash" onClick={() => setSelectedAsset({
            symbol: 'KRW',
            name: '원화 현금',
            type: 'Cash',
            exchange: 'Internal'
          })}>+ 원화 현금 추가</button>
          <button className="btn-usd" onClick={() => setSelectedAsset({
            symbol: 'USD',
            name: '달러 현금',
            type: 'Cash',
            exchange: 'Internal'
          })}>+ 달러 현금 추가</button>
        </div>

        {searchResults.length > 0 && (
          <div className="search-results">
            <h4>검색 결과:</h4>
            <ul>
              {searchResults.map(result => (
                <li 
                  key={result.symbol} 
                  className={selectedAsset?.symbol === result.symbol ? 'selected' : ''}
                  onClick={() => setSelectedAsset(result)}
                >
                  <strong>{result.symbol}</strong> - {result.name} ({result.type}, {result.exchange})
                </li>
              ))}
            </ul>
          </div>
        )}

        {selectedAsset && (
          <div className="add-form">
            <p>선택됨: <strong>{selectedAsset.name} ({selectedAsset.symbol})</strong></p>
            <input 
              type="number" 
              step="any"
              placeholder="보유 수량 입력" 
              value={quantity} 
              onChange={e => setQuantity(e.target.value)}
            />
            <button className="btn-add" onClick={handleAddAsset}>추가하기</button>
          </div>
        )}
      </section>

      <section className="asset-list">
        <div className="section-header">
          <h3>내 자산 현황</h3>
          {data && (
            <button className="btn-ai" onClick={() => {
              const totalValue = data.total_value_krw.toLocaleString();
              const exchangeRate = data.exchange_rate.toFixed(2);
              const assetSummary = data.assets.map(a => 
                `- ${a.name} (${a.symbol}): ${a.quantity}주, 현재가 ${a.current_price.toLocaleString()}, 평가액 ${a.value_krw.toLocaleString()}원 (비중 ${((a.value_krw / data.total_value_krw) * 100).toFixed(1)}%)`
              ).join('\n');
              
              const prompt = `내 주식 자산 포트폴리오를 분석해줘. 나는 현재 30대 초반이야.

[현재 요약]
- 총 평가액: ${totalValue} KRW
- 환율: ${exchangeRate} (USD/KRW)

[자산 상세 내역]
${assetSummary}

위 데이터를 바탕으로, 특히 30대 초반이라는 내 나이와 생애 주기를 고려해서 현재 내 포트폴리오의 분산 투자 정도, 자산 비중의 적절성, 그리고 향후 자산 형성을 위한 투자 전략에 대한 의견을 전문적으로 알려줘.`;
              
              navigator.clipboard.writeText(prompt);
              alert("현재 자산 분석용 AI 프롬프트가 복사되었습니다! Gemini나 ChatGPT에 붙여넣어 보세요.");
            }}>🤖 현재 자산 AI 분석</button>
          )}
        </div>
        {loading ? <p>로딩 중...</p> : (
          <table>
            <thead>
              <tr>
                <th>자산명</th>
                <th>심볼</th>
                <th>수량</th>
                <th>현재가</th>
                <th>평가액 (KRW)</th>
                <th>비중 (%)</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              {data?.assets
                .slice()
                .sort((a, b) => b.value_krw - a.value_krw)
                .map(asset => (
                <tr key={asset.id}>
                  <td>{asset.name}</td>
                  <td>{asset.symbol}</td>
                  <td>
                    {editingId === asset.id ? (
                      <input 
                        type="number" 
                        step="any"
                        className="edit-input"
                        value={editQuantity} 
                        onChange={e => setEditQuantity(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      asset.quantity
                    )}
                  </td>
                  <td>{asset.current_price.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                  <td>{asset.value_krw.toLocaleString()}</td>
                  <td>
                    {data.total_value_krw > 0 
                      ? ((asset.value_krw / data.total_value_krw) * 100).toFixed(1) 
                      : '0.0'}%
                  </td>
                  <td className="actions">
                    {editingId === asset.id ? (
                      <>
                        <button className="btn-save" onClick={() => handleUpdateAsset(asset.id)}>저장</button>
                        <button className="btn-cancel" onClick={() => setEditingId(null)}>취소</button>
                      </>
                    ) : (
                      <>
                        <button className="btn-edit" onClick={() => {
                          setEditingId(asset.id);
                          setEditQuantity(asset.quantity.toString());
                        }}>수정</button>
                        <button className="btn-delete" onClick={() => handleDeleteAsset(asset.id)}>삭제</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="asset-history">
        <h3>자산 변화 이력 (일일 기록)</h3>
        <div className="history-list">
          <table>
            <thead>
              <tr>
                <th>날짜</th>
                <th>총 평가액 (KRW)</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {history.slice().reverse().map(h => (
                <tr key={h.date}>
                  <td>{h.date}</td>
                  <td>{h.total_value_krw.toLocaleString()}</td>
                  <td>
                    <button className="btn-compare" onClick={() => handleCompare(h.date)}>📊 현재와 비교</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {comparison && data && (
        <section id="comparison-report" className="comparison-report">
          <div className="report-header">
            <h3>📈 [{comparison.date}] 대비 자산 변동 리포트</h3>
            <button className="btn-close" onClick={() => setComparison(null)}>닫기</button>
          </div>
          <div className="report-list">
            {data.assets.map(current => {
              const past = comparison.details.find(d => d.symbol === current.symbol);
              if (!past) return null;

              const priceDiff = current.current_price - past.price;
              const pricePercent = (priceDiff / past.price) * 100;
              const valueDiff = current.value_krw - past.value_krw;

              if (Math.abs(priceDiff) < 0.0001 && Math.abs(valueDiff) < 1) return null;

              return (
                <div key={current.id} className={`report-item ${priceDiff > 0 ? 'positive' : 'negative'}`}>
                  <span className="report-name">{current.name}</span>
                  <span className="report-price">
                    <span className="percent">{priceDiff > 0 ? '+' : ''}{pricePercent.toFixed(2)}%</span>
                    <span className="price-diff">({priceDiff > 0 ? '+' : ''}{priceDiff.toLocaleString()} {current.symbol.endsWith(".KS") ? '원' : '$'})</span>
                  </span>
                  <span className="report-value">
                    평가액 변동: <strong>{valueDiff > 0 ? '+' : ''}{valueDiff.toLocaleString()} KRW</strong>
                  </span>
                </div>
              );
            })}
          </div>
          {data.assets.filter(current => {
            const past = comparison.details.find(d => d.symbol === current.symbol);
            return past && (Math.abs(current.current_price - past.price) > 0.0001 || Math.abs(current.value_krw - past.value_krw) > 1);
          }).length === 0 && (
            <p className="no-report">해당 시점 대비 변동된 자산이 없습니다.</p>
          )}
        </section>
      )}
    </div>
  )
}

export default App
