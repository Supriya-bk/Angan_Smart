import { motion } from "framer-motion";

function Home() {
  return (
    <div className="container mt-5">
      <motion.div
        whileHover={{ scale: 1.05 }}
        className="card p-4 shadow"
      >
        <h4>👶 Total Children: 120</h4>
      </motion.div>
    </div>
  );
}

export default Home;