import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FaHome, FaBox, FaHeartbeat, FaUser,
  FaBell, FaChartBar
} from "react-icons/fa";

const menu = [
  { name: "Home", path: "/home", icon: <FaHome /> },
  { name: "Inventory", path: "/inventory", icon: <FaBox /> },
  { name: "Attendance", path: "/attendance", icon: <FaHeartbeat /> },
  { name: "Health", path: "/health", icon: <FaUser /> },
  { name: "SOS", path: "/sos", icon: <FaBell /> },
  { name: "Dashboard", path: "/dashboard", icon: <FaChartBar /> },
];

function Sidebar() {
  return (
    <div className="sidebar">
      <h3 className="logo">Anganwadi 🚀</h3>

      {menu.map((item, i) => (
        <motion.div key={i} whileHover={{ scale: 1.1 }}>
          <Link to={item.path} className="menu-btn">
            {item.icon} {item.name}
          </Link>
        </motion.div>
      ))}
    </div>
  );
}

export default Sidebar;