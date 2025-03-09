import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "./ui/card";
import { Loader2, CheckCircle, Upload } from "lucide-react";
import axios from "axios";
import { BASE_URL } from "../others/APIs";


function FaceRecognition() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const videoRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const videoStreamRef = useRef(null);
  const [isMobile, setIsMobile] = useState(false);
  let queue;

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      event.target.value = '';
    }
  };

  useEffect(() => {
    setIsMobile(window.innerWidth <= 768);
  }, []);

  useEffect(() => {
    if (selectedImage) {
      setImagePreview(URL.createObjectURL(selectedImage));
      verifyImage();
    }
  }, [selectedImage]);

  const verifyImage = async () => {
    setLoading(true);
    setVerificationStatus(null);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      await axios.post(`${BASE_URL}/detect_face`, formData);
      startCamera();
    } catch (error) {
      setSelectedImage(null);
      setImagePreview(null);
      setErrorMessage(error?.response?.data?.error || "Error verifying image.");
      setTimeout(() => setErrorMessage(""), 2000);
    }
    setLoading(false);
  };

  const stopCamera = () => {
    if (videoStreamRef.current) {
      videoStreamRef.current.getTracks().forEach(track => track.stop());
      videoStreamRef.current = null;
    }
  };

  const startCamera = async () => {
    setStreaming(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoStreamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
        };
      } else {
        console.error("Video is NULL!");
        setErrorMessage("Could not access camera.");
        setTimeout(() => setErrorMessage(""), 2000);
        resetAll();
      }

      captureFrames();
    } catch (error) {
      setErrorMessage("Could not access camera.");
      setTimeout(() => setErrorMessage(""), 2000);
      resetAll();
    }
  };

  const resetAll = () => {
    setVerificationStatus(null);
    setImagePreview(null);
    setSelectedImage(null);
    setStreaming(false);
    stopCamera();
    queue = false;
  };

  const captureFrames = () => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const interval = setInterval(async () => {
      if (queue) return;
      if (!videoRef.current) return;
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("image", selectedImage);
        formData.append("frame", blob);
        try {
          queue = true;
          const response = await axios.post(`${BASE_URL}/compare_faces`, formData);
          console.log('Response:', response)
          setVerificationStatus(response.data.matched ? "verified" : "not_verified");
          setTimeout(() => {
            resetAll();
          }, 1500);
          if (interval) {
            clearInterval(interval);
          };
        } catch (error) {
          queue = false;
          setErrorMessage(error?.response?.data?.error ? error?.response?.data?.error : "Error verifying frames.");
          setTimeout(() => setErrorMessage(""), 2000);
          resetAll();
        }
      }, "image/jpeg");
    }, 3000);
  };

  return (
    <div className="min-h-screen w-full bg-gray-900 text-white p-6 flex flex-col items-center">
      <motion.h1
        className="text-4xl font-bold text-center mt-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{fontSize: isMobile ? '2.5em' : '3.2em'}}
      >
        Face Recognition
      </motion.h1>

      <div className="mt-8 flex flex-col md:flex-row items-center justify-center gap-6 w-full max-w-3xl">
        <Card className="p-4 text-center border-2 border-gray-700 w-full md:w-1/2" style={{ cursor: "auto" }}>
          <CardContent style={{ display: "flex", flexDirection: "column", alignItems: "center", cursor: "auto" }}>
            <input type="file" accept="image/*" disabled={streaming || loading} onChange={(e) => streaming || loading ? null : handleImageUpload(e)} className="hidden" id="upload" />
            <label htmlFor="upload" className="cursor-pointer flex items-center gap-2 p-2 rounded-lg text-white" style={{ backgroundColor: "oklch(0.28 0.03 257.69)", border: "1px solid white", cursor: streaming || loading ? "auto" : "pointer" }}>
              <Upload /> Upload Image
            </label>
            {imagePreview && <img src={imagePreview} alt="Preview" className="mt-4 rounded-lg h-auto object-contain" style={{ width: "150px", height: "150px" }} />}
          </CardContent>
        </Card>

        {streaming && (
          <Card className="relative p-4 text-center border-2 border-gray-700 w-full md:w-1/2">
            <div className="relative w-full flex flex-col items-center" style={{height: "207px"}}>
              <div className="relative w-full max-w-xs md:max-w-full h-48 md:h-64 bg-black rounded-lg overflow-hidden">
                <video ref={videoRef} autoPlay className="w-full h-full" />

                <motion.div
                  className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent via-green-400 to-transparent opacity-60"
                  initial={{ y: "-100%" }}
                  animate={{ y: "100%" }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />

                {[...Array(5)].map((_, index) => (
                  <motion.div
                    key={index}
                    className="absolute w-2 h-2 bg-green-400 rounded-full"
                    style={{
                      top: `${Math.random() * 80 + 10}%`,
                      left: `${Math.random() * 80 + 10}%`,
                    }}
                    animate={{
                      opacity: [0, 1, 0],
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: index * 0.5,
                    }}
                  />
                ))}
              </div>

              <motion.p
                className="mt-4 text-gray-300"
                animate={{ opacity: streaming ? [0, 1, 0] : 1 }}
                transition={{ duration: 1.5, repeat: streaming ? Infinity : 0 }}
              >
                Verifying face...
              </motion.p>
            </div>
          </Card>
        )}
      </div>

      {loading && <Loader2 className="animate-spin mt-4 text-white" size={32} />}

      {verificationStatus && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className={`mt-4 px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 ${verificationStatus === "verified" ? "bg-green-500" : "bg-white-500 border border-white"}`}
        >
          {verificationStatus === "verified" ? <CheckCircle /> : "❌"} {verificationStatus === "verified" ? "Verified!" : "Not Verified!"}
        </motion.div>
      )}

      {errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg"
        >
          {errorMessage}
        </motion.div>
      )}
    </div>

  );
}

export default FaceRecognition;
