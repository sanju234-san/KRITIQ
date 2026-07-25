import HistoryHeader from "../components/history/HistoryHeader";
import HistoryFilters from "../components/history/HistoryFilters";
import Timeline from "../components/history/Timeline";
import RightSidebar from "../components/history/RightSidebar";
import { historyData } from "../components/history/historyData";

const History = () => {
  return (
    <div className="min-h-screen bg-[#0F1723] px-6 py-8">
      <HistoryHeader />

      <HistoryFilters />

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
        {/* Left Content */}
        <div className="xl:col-span-2">
          <Timeline history={historyData} />
        </div>

        {/* Right Sidebar */}
        <div>
          <RightSidebar />
        </div>
      </div>
    </div>
  );
};

export default History;