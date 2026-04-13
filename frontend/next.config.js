/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    // Allow images from carsensor.net and its CDN
    remotePatterns: [
      { protocol: "https", hostname: "**.carsensor.net" },
      { protocol: "https", hostname: "carsensor.net" },
      { protocol: "http", hostname: "**.carsensor.net" },
    ],
  },
};

module.exports = nextConfig;
