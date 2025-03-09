import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Loader2, CheckCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import axios from "axios";
import { BASE_URL } from "../others/APIs";


function CustomTooltip({ active, payload, label, secondLabel = 'Posts' }) {
  if (active && payload && payload.length) {
    const { value, payload: data } = payload[0];
    return (
      <div className="bg-gray-900 text-white p-2 rounded shadow-lg border border-gray-700">
        <p className="text-sm font-bold">Date: {label}</p>
        <p className="text-sm">{secondLabel}: {value}</p>
      </div>
    );
  }
  return null;
}

function InstaAnalytics() {
  const [username, setUsername] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isMobile, setIsMobile] = useState(false);
  const [last30pLikes, setLast30pLikes] = useState([]);
  const [last30pComments, setLast30pComments] = useState([]);

  useEffect(() => {
    setIsMobile(window.innerWidth <= 768);
  }, []);

  const fetchData = async () => {
    setMessage('');
    if (!username.trim()) {
      setError("Please enter a valid username!");
      setTimeout(() => setError(""), 2000);
      return;
    }
    setLoading(true);
    setData(null);
    setError("");

    try {
      const response = await axios.post(`${BASE_URL}/insta-analytics`, {'username': username.trim()});
      if (Object.keys(response.data).length > 0){
        setData(response.data);
        setLast30pLikes(response.data.analytics.last_30p_likes);
        setLast30pComments(response.data.analytics.last_30p_comments);
      }
      else{
        setMessage('Data not found');
      };
    } catch (err) {
      console.log('Error:', err);
      setError(err?.response?.data?.error || "Failed to fetch data. Try again!");
      setTimeout(() => setError(""), 2000);
    };
    setLoading(false);
  };

  return (
    <div className="min-h-screen w-full bg-gray-900 text-white p-6 flex flex-col items-center">
      <motion.h1 style={{fontSize: isMobile ? '2.5em' : '3.2em'}} className="text-4xl font-bold text-center mt-6" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        Instagram Analytics
      </motion.h1>
      
      <Input
        type="text"
        placeholder="Enter Instagram Username"
        className={`mt-6 p-3 text-white border border-white rounded-lg w-full max-w-lg bg-transparent placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-white 
          ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
        value={username}
        onChange={(e) => !loading && setUsername(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && fetchData()}
        disabled={loading}
      />
      
      <Button onClick={()=> !loading && fetchData()} style={{ backgroundColor: "oklch(0.54 0.05 264.51 / 0.5)", cursor: loading && "progress", pointerEvent: loading && "none", color: loading && "gray" }} disabled={loading} className="mt-4 bg-blue-500 text-white px-6 py-3 rounded-lg">
        Fetch Data
      </Button>
      
      {loading && <Loader2 className="animate-spin mt-6 w-12 h-12" />}

      {message && <p style={{marginTop: '30px', fontSize: '20px', fontWeight: 'bold'}}>{message}</p>}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg"
        >
          {error}
        </motion.div>
      )}

      {data && (
        <div className="mt-6 w-full max-w-4xl">
          <a href={`https://www.instagram.com/${data.profile.username}`} target="_blank" rel="noopener noreferrer">
            <Card className="p-4 flex items-center gap-4 bg-gray-800 rounded-lg">
              <img 
                src={`${BASE_URL}/fetch-image?url=${encodeURIComponent(data.profile.profile_pic)}`} 
                alt="Profile" 
                className="w-16 h-16 rounded-full" 
              />
              <div>
                <h2 className="text-xl font-bold flex items-center gap-1">
                  {data.profile.full_name}
                  {data.profile.is_verified && <CheckCircle className="text-blue-500 w-5 h-5" />}
                </h2>
                <p>@{data.profile.username}</p>
                <p>{data.profile.biography}</p>
              </div>
            </Card>
          </a>

          <div className="grid grid-cols-3 gap-4 mt-6">
            <Card className="p-4 text-center bg-gray-800 rounded-lg" style={{flexDirection: "column", display: "flex", justifyContent: "center", alignItems: "center"}}>
              <h3 className="text-base sm:text-lg font-bold">Followers</h3>
              <p>{data.profile.followers}</p>
            </Card>
            <Card className="p-4 text-center bg-gray-800 rounded-lg" style={{flexDirection: "column", display: "flex", justifyContent: "center", alignItems: "center"}}>
              <h3 className="text-base sm:text-lg font-bold">Following</h3>
              <p>{data.profile.followings}</p>
            </Card>
            <Card className="p-4 text-center bg-gray-800 rounded-lg" style={{flexDirection: "column", display: "flex", justifyContent: "center", alignItems: "center"}}>
              <h3 className="text-base sm:text-lg font-bold">Total Posts</h3>
              <p>{data.profile.posts}</p>
            </Card>
          </div>

          {data.latest_post && data.latest_post.post_media && (
            <a href={data.latest_post.post_url} target="_blank" rel="noopener noreferrer">
              <Card className="p-4 bg-gray-800 rounded-lg flex flex-col items-center mt-6">
                <h3 className="text-base sm:text-lg font-bold">Latest Post</h3>
                <img
                  src={`${BASE_URL}/fetch-image?url=${encodeURIComponent(data.latest_post.post_media)}`}
                  alt="Latest Post"
                  className="w-full h-48 object-contain rounded-lg mt-2"
                />
                <p className="text-sm sm:text-base">{data.latest_post.likes} Likes</p>
                <p className="text-sm sm:text-base">{data.latest_post.comments} Comments</p>
              </Card>
            </a>
          )}

          <Card className="p-4 bg-gray-800 rounded-lg text-center mt-6">
            <p className="text-gray-300 text-sm" style={{fontWeight: 'bold'}}>Total likes and comments from the Last 30 Posts</p>
          </Card>

          <div className="grid grid-cols-2 gap-4 mt-6">
            <Card className="p-4 text-center bg-gray-800 rounded-lg" style={{flexDirection: "column", display: "flex", justifyContent: "center", alignItems: "center"}}>
              <h3 className="text-base sm:text-lg font-bold">Total Likes</h3>
              <p>{data.analytics.total_likes}</p>
            </Card>
            <Card className="p-4 text-center bg-gray-800 rounded-lg" style={{flexDirection: "column", display: "flex", justifyContent: "center", alignItems: "center"}}>
              <h3 className="text-base sm:text-lg font-bold">Total Comments</h3>
              <p>{data.analytics.total_comments}</p>
            </Card>
          </div>
          
          <Card className="p-4 bg-gray-800 rounded-lg text-center mt-6">
            <p className="text-gray-300 text-sm" style={{fontWeight: 'bold'}}>📊 Activity Overview from the Last 30 Days</p>
          </Card>

          <div className="mt-6 bg-gray-800 p-4 rounded-lg">
            <h3 className="text-lg font-bold mb-4">Posting Frequency Trend (Last 30 Days)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={Object.entries(data.analytics.last_30d_post_frequency).map(([date, count]) => ({ date, count }))}>
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis 
                  domain={[0, 'dataMax']} 
                  allowDecimals={false} 
                />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="count" stroke="#00c0ff" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <Card className="p-4 bg-gray-800 rounded-lg text-center mt-6">
            <p className="text-gray-300 text-sm" style={{fontWeight: 'bold'}}>📊 Performance Insights from the Last 30 Posts</p>
          </Card>

          <div className="mt-6 bg-gray-800 p-4 rounded-lg">
            <h3 className="text-lg font-bold mb-4">Engagement Trend (Likes)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart onClick={(e) => {
                if (e && e.activePayload && e.activePayload.length) {
                  const clickedData = e.activePayload[0].payload;
                    if (clickedData.post) {
                      window.open(clickedData.post, '_blank');
                    }
                  }
                }}
                data={last30pLikes}
              >
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 'dataMax']} allowDecimals={false} />
              <Tooltip content={<CustomTooltip secondLabel="Likes" />} />
              <Line type="monotone" dataKey="likes" stroke="#ff7300" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
          </div>
          
          <div className="mt-6 bg-gray-800 p-4 rounded-lg">
            <h3 className="text-lg font-bold mb-4">Engagement Trend (Comments)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart onClick={(e) => {
                if (e && e.activePayload && e.activePayload.length) {
                  const clickedData = e.activePayload[0].payload;
                    if (clickedData.post) {
                      window.open(clickedData.post, '_blank');
                    }
                  }
                }}
                data={last30pComments}
                >
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 'dataMax']} allowDecimals={false} />
                <Tooltip content={<CustomTooltip secondLabel="Comments" />} />
                <Line type="monotone" dataKey="comments" stroke="#ff7300" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
            <a href={data.analytics.most_liked_post.post_url} target="_blank" rel="noopener noreferrer">
              <Card className="p-4 bg-gray-800 rounded-lg flex flex-col items-center">
                <h3 className="text-base sm:text-lg font-bold">Most Liked Post</h3>
                <img
                  src={`${BASE_URL}/fetch-image?url=${encodeURIComponent(data.analytics.most_liked_post.post_media)}`}
                  alt="Most Liked"
                  className="w-full h-48 object-contain rounded-lg mt-2"
                />
                <p className="text-sm sm:text-base">{data.analytics.most_liked_post.likes} Likes</p>
              </Card>
            </a>

            <a href={data.analytics.most_commented_post.post_url} target="_blank" rel="noopener noreferrer">
              <Card className="p-4 bg-gray-800 rounded-lg flex flex-col items-center">
                <h3 className="text-base sm:text-lg font-bold">Most Commented Post</h3>
                <img
                  src={`${BASE_URL}/fetch-image?url=${encodeURIComponent(data.analytics.most_commented_post.post_media)}`}
                  alt="Most Commented"
                  className="w-full h-48 object-contain rounded-lg mt-2"
                />
                <p className="text-sm sm:text-base">{data.analytics.most_commented_post.comments} Comments</p>
              </Card>
            </a>
          </div>

        </div>
      )}
    </div>
  );
}

export default InstaAnalytics;
