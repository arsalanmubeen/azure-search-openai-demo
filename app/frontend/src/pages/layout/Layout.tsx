import { Outlet, NavLink, Link } from "react-router-dom";

import github from "../../assets/QDS_LOGO.png";

import styles from "./Layout.module.css";

import { useLogin } from "../../authConfig";

import { LoginButton } from "../../components/LoginButton";

const Layout = () => {
    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <Link to="/" className={styles.headerTitleContainer}>
                        <h3 className={styles.headerTitle}>GPT + Enterprise data | QDS Knowledge Base</h3>
                    </Link>
                    <nav>
                        <ul className={styles.headerNavList}>
                            <li>
                                <NavLink to="/" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                                    Chat
                                </NavLink>
                            </li>
                            <li className={styles.headerNavLeftMargin}>
                                <NavLink to="/qa" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                                    Ask a question
                                </NavLink>
                            </li>
                        </ul>
                    </nav>
                    <h4 className={styles.headerTitle}>Azure OpenAI + Cognitive Search</h4>
                    <ul className={styles.headerNavList}>
                        <li className={styles.headerNavLeftMargin}>
                            <a href="https://www.qdsnet.com" target={"_blank"} title="Qatar Datamation System">
                                <img src={github} alt="QDS logo" aria-label="Link to QDS Website" width="100px" height="60px" className={styles.githubLogo} />
                            </a>
                        </li>
                    </ul>
                    {useLogin && <LoginButton />}
                </div>
            </header>

            <Outlet />
        </div>
    );
};

export default Layout;
