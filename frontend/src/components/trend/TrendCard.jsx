function TrendCard({ item }) {
  return (
    <div className="border rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition">
      {/* 이미지 영역 */}
      <div className="w-full h-40 bg-gray-100 flex items-center justify-center">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.title || "상표 이미지"}
            className="w-full h-full object-contain"
          />
        ) : (
          <span className="text-gray-400 text-sm">이미지 없음</span>
        )}
      </div>

      {/* 정보 영역 */}
      <div className="p-3">
        <p className="font-medium text-sm truncate">
          {item.title || "(상표명 없음)"}
        </p>
        <p className="text-xs text-gray-600 mt-1">{item.applicant_name}</p>
        <p className="text-xs text-gray-400 mt-1">{item.application_date}</p>
      </div>
    </div>
  );
}

export default TrendCard;
