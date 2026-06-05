function TrendSort({ sort, onSortChange }) {
  const options = [
    { value: "latest", label: "최신순" },
    { value: "oldest", label: "오래된순" },
    { value: "applicant", label: "출원인순" },
  ];

  return (
    <div className="flex flex-col">
      <label className="text-sm font-medium text-gray-700 mb-1">정렬</label>
      <select
        value={sort}
        onChange={(e) => onSortChange(e.target.value)}
        className="h-10 px-3 rounded-md border border-gray-300 bg-white text-gray-700 min-w-[140px] focus:outline-none focus:border-blue-500 transition"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export default TrendSort;
