import TrendCard from "./TrendCard";

function TrendGrid({ items }) {
  if (!items || items.length === 0) {
    return (
      <p className="text-center text-gray-500 py-10">데이터가 없습니다.</p>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {items.map((item) => (
        <TrendCard key={item.id} item={item} />
      ))}
    </div>
  );
}

export default TrendGrid;
