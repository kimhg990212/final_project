import { useEffect, useState } from "react";
import { getTrends } from "../api/trend";
import TrendGrid from "../components/trend/TrendGrid";

function TrendPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrends({ period: "1y", page: 1 })
      .then((response) => {
        setData(response);
        setLoading(false);
      })
      .catch((error) => {
        console.error("API 호출 실패:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">업종별 트렌드</h1>
      {loading ? (
        <p className="text-center py-10">로딩 중...</p>
      ) : (
        <TrendGrid items={data?.data} />
      )}
    </div>
  );
}

export default TrendPage;
