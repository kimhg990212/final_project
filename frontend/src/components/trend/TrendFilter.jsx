function TrendFilter({ period, onPeriodChange }) {
  const options = [
    { value: "6m", label: "6개월" },
    { value: "1y", label: "1년" },
    { value: "3y", label: "3년" },
  ];

  return (
    <div className="flex flex-col">
      <label className="text-sm font-medium text-gray-700 mb-1">기간</label>
      <div className="flex gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onPeriodChange(option.value)}
            className={`h-10 px-4 rounded-md border transition ${
              // 삼항 연산자 사용
              period === option.value
                ? "bg-purple-100 text-purple-800 border-purple-500 font-semibold"
                : "bg-white text-gray-700 border-gray-300 hover:bg-purple-50"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default TrendFilter;
