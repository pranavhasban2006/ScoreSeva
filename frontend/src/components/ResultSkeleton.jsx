export default function ResultSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Top Header Placeholder */}
      <div className="card text-center space-y-6 py-12 flex flex-col items-center justify-center">
        <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-4 border-gray-100"></div>
          <div className="absolute inset-0 rounded-full border-4 border-orange-500 border-t-transparent animate-spin"></div>
          <span className="text-3xl">✨</span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Generating Score...</h3>
          <p className="text-sm text-gray-500 mt-1">Analyzing applicant profile and alternative data</p>
        </div>
      </div>
      
      {/* Main Body Placeholder */}
      <div className="card space-y-4">
        <div className="w-full h-12 bg-gray-200 rounded-xl"></div>
        <div className="w-full h-8 bg-gray-200 rounded-lg"></div>
        <div className="w-3/4 h-8 bg-gray-200 rounded-lg"></div>
        <div className="w-full h-8 bg-gray-200 rounded-lg"></div>
      </div>
      
      {/* Footer Cards Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card space-y-3 h-32">
          <div className="w-1/2 h-5 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
        </div>
        <div className="card space-y-3 h-32">
          <div className="w-1/2 h-5 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  );
}
