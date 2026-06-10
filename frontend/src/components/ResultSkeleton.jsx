export default function ResultSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Top Header Placeholder */}
      <div className="card text-center space-y-4 py-8">
        <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto"></div>
        <div className="w-48 h-6 bg-gray-200 rounded-full mx-auto mt-4"></div>
        <div className="w-32 h-4 bg-gray-200 rounded-full mx-auto mt-2"></div>
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
