import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import WebScraping from "./components/WebScraping";
import FaceRecognition from "./components/FaceRecognition";
import NotFound from "./components/NotFound";
import InstaAnalytics from "./components/InstaAnalytics";
import SentimentAnalyzer from "./components/SentimentAnalyzer";


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/web-scraping" element={<WebScraping />} />
        <Route path="/face-recognition" element={<FaceRecognition />} />
        <Route path="/insta-analytics" element={<InstaAnalytics />} />
        <Route path="/sentiment-analyzer" element={<SentimentAnalyzer />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default App;
