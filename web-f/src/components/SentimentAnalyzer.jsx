import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Input } from "./ui/input";
import { Loader2, Eye } from "lucide-react";
import axios from "axios";
import { BASE_URL } from "../others/APIs";


function SentimentAnalyzer() {
  const [analyzers, setAnalyzers] = useState([]);
  const [selectedAnalyzer, setSelectedAnalyzer] = useState(null);
  const [searchKey, setSearchKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState([]);
  const [noResult, setNoResult] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 7;
  const [tableKeys, setTableKeys] = useState([]);
  const [lastSelectedScraper, setLastSelectedScraper] = useState("");
  const [loadingMessage, setLoadingMessage] = useState("");
  const [expandedCell, setExpandedCell] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  const fetchScrapers = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/sentiment-analyzers`);
      setAnalyzers(response.data);
    }
    catch (error) {
      console.log('Error:', error);
      setErrorMessage('Something went wrong');
    };
  };

  useEffect(() => {
    fetchScrapers();
  }, []);

  useEffect(() => {
    setIsMobile(window.innerWidth <= 768);
  }, []);
  
  const handleCellClick = (indexP, index) => {
    if (isMobile) {
      setExpandedCell((prev) => (prev?.row === indexP && prev?.col === index ? null : { row: indexP, col: index }));
    }
  };

  const loadingMessages = [
    "Almost there... stay tuned!",
    "Cooking up some fresh results! 🍲",
    "Hold on tight, it's coming! 🚀",
    "The internet gods are working hard... ⏳",
    "Scraping with love... just a moment! ❤️",
    "Fetching the best results for you! 🔍",
    "Loading... meanwhile, take a deep breath! 😌",
    "Results are marinating... almost ready! 🍛",
    "Hacking... just kidding, scraping data! 😜",
    "Tuning into the internet waves... 📡",
    "Searching... this ain't Google, but close! 😆",
    "Your patience level is impressive! ⏳🔥",
    "Loading... grab a coffee meanwhile! ☕",
    "If we had a rupee for every second... 💸",
    "Processing... hope you’re comfy! 🛋️",
    "Good things take time... and some CPU power! 🖥️",
    "Hold on... AI needs a sec to think! 🤖",
    "Scraping faster than your ex moved on! 😂",
    "Finding the needle in the digital haystack! 📦",
    "Summoning data spirits... please wait! 👻",
  ];

  useEffect(() => {
    setExpandedCell(null);
    let messageTimer;
    let interval;

    if (loading) {
      messageTimer = setTimeout(() => {
        let index = 0;
        setLoadingMessage(loadingMessages[index]);
        interval = setInterval(() => {
          index = (index + 1) % loadingMessages.length;
          setLoadingMessage(loadingMessages[index]);
        }, 5000);
      }, 10000);
    }

    return () => {
      if (messageTimer) clearTimeout(messageTimer);
      if (interval) clearInterval(interval);
      setLoadingMessage("");
    };
  }, [loading]);

  const handleSearch = async () => {
    if (!selectedAnalyzer || !searchKey.trim()) {
      setErrorMessage("Please select a scraper and enter a search keyword!");
      setTimeout(() => setErrorMessage(""), 2000);
      return;
    };

    if (searchKey.trim().length < 3){
      setErrorMessage("Search keyword must be at least 3 characters long!");
      setTimeout(() => setErrorMessage(""), 2000);
      return;
    };

    setResult([]);
    setNoResult("");
    setLastSelectedScraper("");
    setLoading(true);

    try {
      const search_from = selectedAnalyzer;
      const response = await axios.post(`${BASE_URL}/scrape`, {
        search_key: searchKey,
        search_from: search_from,
      });
      console.log('Response:', response);
      if (response.data && response.data.length > 0) {
        setLastSelectedScraper(search_from);
        setResult(response.data);
        setCurrentPage(1);
        const keys = Object.keys(response.data[0]);
        setTableKeys(keys);
      }
      else {
        setNoResult('No result');
      };
      setLoading(false);
    }
    catch (error) {
      console.log('Error:', error);
      setErrorMessage('Something went wrong');
      setTimeout(() => setErrorMessage(""), 3000);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gray-900 text-white p-6 flex flex-col items-center">
      <motion.h1
      style={{fontSize: isMobile ? '2.5em' : '3.2em'}}
        className="text-4xl font-bold text-center mt-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Sentiment Analyzer
      </motion.h1>

      <div
        className={`mt-8 grid gap-4 w-full max-w-4xl ${analyzers.length === 1 ? "grid-cols-1 place-items-center" : "grid-cols-1 sm:grid-cols-2 md:grid-cols-4"}`}
      >
        {analyzers.map((scraperObj, index) => {
          const [name, value] = Object.entries(scraperObj)[0];

          return (
            <motion.div whileTap={{ scale: loading ? 1 : 0.9 }} key={index}>
              <Card
                className={`p-4 text-center cursor-pointer rounded-lg transition-all duration-300 border-2 ${selectedAnalyzer === value ? "border-blue-500" : "border-gray-700"
                  } ${loading ? "cursor-progress opacity-50" : ""}`}
                style={{ cursor: loading ? "progress" : "pointer", width: analyzers.length === 1 ? "300px" : "auto" }}
                onClick={() => !loading && setSelectedAnalyzer(value)}
              >
                <CardContent>{name}</CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <Input
        type="text"
        placeholder="Enter a video url"
        className={`mt-6 p-3 text-white border border-white rounded-lg w-full max-w-lg bg-transparent placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-white 
        ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
        value={searchKey}
        onChange={(e) => !loading && setSearchKey(e.target.value)}
        disabled={loading}
        onKeyDown={(e) => e.key === "Enter" && !loading && handleSearch()}
      />

      <Button
        onClick={() => !loading && handleSearch()}
        disabled={loading}
        className="mt-4 bg-blue-500 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-all duration-300"
        style={{ backgroundColor: "oklch(0.54 0.05 264.51 / 0.5)", cursor: loading && "progress", pointerEvent: loading && "none", color: loading && "gray" }}
      >
        Analyze
      </Button>

      {
        loading && <Loader2 className="animate-spin mt-6 w-12 h-12" />
      }

      {result.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mt-6 w-full max-w-4xl"
        >
          <span className="text-gray-400 text-xs ml-1">*{isMobile ? "Click on" : "Hover over"} a {lastSelectedScraper != "g-news" ? "Name" : "Title"} {lastSelectedScraper === "flipkart" && "or Description"} to view the full text</span>
          <div className="w-full overflow-x-auto">
            <table className="w-full border-collapse bg-gray-800 text-white shadow-lg rounded-lg">
              <thead>
                <tr style={{ backgroundColor: "oklch(0.54 0.05 264.51 / 0.5)" }}>
                  {tableKeys.map((key, index) => (
                    <th key={index} className="p-3 text-center w-1/5">{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result
                  .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                  .map((item, indexP) => (
                    <motion.tr
                      key={item.id}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: indexP * 0.1 }}
                      className="border-b border-gray-700 hover:bg-gray-700 transition"
                    >
                      {Object.values(item).map((value, index) => (
                        <td className="p-3 w-1/5 text-center" key={index} onClick={() => handleCellClick(indexP, index)}>
                          {
                            lastSelectedScraper != "g-news" ?
                            <>
                              {
                                tableKeys[index] === "Name" && (
                                  <>
                                  <div className="relative group hidden sm:block">
                                    <span>{value ? String(value).slice(0, 10) + "..." : "-"}</span>
                                    {value && (
                                      <div className="absolute z-10 hidden group-hover:block bg-black text-white text-xs p-2 rounded-lg max-w-xs whitespace-normal break-words shadow-lg w-max"
                                          style={{ left: "50%", transform: "translateX(-50%)", bottom: indexP == 0 ? "" : "100%", marginBottom: "5px" }}>
                                        {value}
                                      </div>
                                    )}
                                  </div>

                                  <div className="sm:hidden">
                                    <span>{expandedCell?.row === indexP && expandedCell?.col === index ? value : String(value)?.slice(0, 10) + "..." || "-"}</span>
                                  </div>
                                  </>
                                )
                              }

                              {tableKeys[index] === "Description" && (
                                <>
                                <div className="relative group hidden sm:block">
                                  <span>{value ? String(value).slice(0, 10) + "..." : "-"}</span>
                                  {value && (
                                    <div className="absolute z-10 hidden group-hover:block bg-black text-white text-xs p-2 rounded-lg max-w-xs whitespace-normal break-words shadow-lg w-max"
                                        style={{ transform: "translateX(-50%)", bottom: indexP == 0 ? "" : "100%", marginBottom: "5px" }}>
                                      {value}
                                    </div>
                                  )}
                                </div>

                                <div className="sm:hidden">
                                  <span>{expandedCell?.row === indexP && expandedCell?.col === index ? value : String(value).slice(0, 10) + "..." || "-"}</span>
                                </div>
                                </>
                              )}

                              {tableKeys[index] === "Image" && (
                                value ? (
                                  <a
                                    href={value}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-block w-10 h-10 text-blue-500 flex justify-center items-center gap-2"
                                  >
                                    <img src={value} className="rounded-sm w-10 h-10 object-cover" />
                                  </a>
                                ) : "-"
                              )}

                              {tableKeys[index] === "Link" && (
                                value ? (
                                  <a
                                    href={value}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-500 flex justify-center items-center gap-2"
                                  >
                                    <Eye className="w-5 h-5" />
                                  </a>
                                ) : "-"
                              )}

                              {tableKeys[index] !== "Name" &&
                                tableKeys[index] !== "Image" &&
                                tableKeys[index] !== "Link" &&
                                tableKeys[index] !== "Description" &&
                                (value ? value : "-")
                              }
                            </>
                            :
                            <>

                              {
                                tableKeys[index] === "Title" && (
                                  <div className="relative group">
                                    <span>{value ? String(value).slice(0, 10) : "-"}</span>
                                    {value && (
                                      <div className="absolute z-10 hidden group-hover:block bg-black text-white text-xs p-2 rounded-lg max-w-xs whitespace-normal break-words shadow-lg w-max"
                                          style={{ left: "50%", transform: "translateX(-50%)", bottom: indexP == 0 ? "" : "100%", marginBottom: "5px" }}>
                                        {value}
                                      </div>
                                    )}
                                  </div>
                                )
                              }

                              {(tableKeys[index] === "Provider") && (
                                value ? (
                                  <a
                                    href={value}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-block w-10 h-10 text-blue-500 flex justify-center items-center gap-2"
                                  >
                                    <img src={value} className={tableKeys[index] === "Provider" ? "rounded-sm w-10 h-10 object-none" : "rounded-sm w-10 h-10 object-cover"} />
                                  </a>
                                ) : "-"
                              )}

                              {(tableKeys[index] === "Link" || tableKeys[index] === "Image") && (
                                value ? (
                                  <a
                                    href={value}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-500 flex justify-center items-center gap-2"
                                  >
                                    <Eye className="w-5 h-5" />
                                  </a>
                                ) : "-"
                              )}

                              {tableKeys[index] !== "Provider" &&
                                tableKeys[index] !== "Image" &&
                                tableKeys[index] !== "Title" &&
                                tableKeys[index] !== "Link" &&
                                (value ? value : "-")
                              }
                            </>
                          }
                          
                        </td>
                      ))}
                    </motion.tr>
                  ))}
              </tbody>
            </table>
          </div>


          {result.length > itemsPerPage && (
            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-700 rounded-md hover:bg-gray-600 disabled:opacity-50"
                style={{ backgroundColor: "oklch(0.54 0.05 264.51 / 0.5)" }}
              >
                Previous
              </button>

              <span className="text-white">Page {currentPage} of {Math.ceil(result.length / itemsPerPage)}</span>

              <button
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, Math.ceil(result.length / itemsPerPage)))}
                disabled={currentPage === Math.ceil(result.length / itemsPerPage)}
                className="px-4 py-2 bg-gray-700 rounded-md hover:bg-gray-600 disabled:opacity-50"
                style={{ backgroundColor: "oklch(0.54 0.05 264.51 / 0.5)" }}
              >
                Next
              </button>
            </div>
          )}
        </motion.div>
      )}

      {errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg"
        >
          {errorMessage}
        </motion.div>
      )}

      {loading && (
        <div className="mt-6 text-center">
          {loadingMessage && <p className="mt-4 text-sm text-gray-300">{loadingMessage}</p>}
        </div>
      )}

      {noResult && <div className="mt-4 p-4 bg-gray-800 rounded-lg w-full max-w-md text-center">{noResult}</div>}

    </div>
  );
}

export default SentimentAnalyzer;
