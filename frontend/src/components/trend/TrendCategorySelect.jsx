import { NICE_CODES } from "../../constants/niceCodes";

function TrendCategorySelect({ classification, onClassificationChange }) {
  return (
    //업종 드롭다운
    <div className="flex flex-col">
      <label className="text-sm font-medium text-gray-700 mb-1">업종</label>
      <select
        value={classification}
        onChange={(e) => onClassificationChange(e.target.value)}
        className="h-10 px-3 rounded-md border border-gray-300 bg-white text-gray-700 min-w-[160px] focus:outline-none focus:border-blue-500 transition"
      >
        {NICE_CODES.map((option) => (
          <option key={option.code} value={option.code}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export default TrendCategorySelect;
