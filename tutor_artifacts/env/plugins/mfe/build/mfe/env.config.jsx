import React, { useEffect, useState } from 'react';
import Cookies from 'universal-cookie';

import { getConfig } from '@edx/frontend-platform';
import { Icon } from '@openedx/paragon';
import { Nightlight, WbSunny } from '@openedx/paragon/icons';
import { useIntl } from '@edx/frontend-platform/i18n';

function addPlugins(config, slot_name, plugins) {
  if (slot_name in config.pluginSlots === false) {
    config.pluginSlots[slot_name] = {
      keepDefault: true,
      plugins: []
    };
  }

  config.pluginSlots[slot_name].plugins.push(...plugins);
}

let themeCookie = 'indigo-toggle-dark';
let themeCookieExpiry = 90; // days

const AddDarkTheme = () => {
  const cookies = new Cookies();
  const isThemeToggleEnabled = getConfig().INDIGO_ENABLE_DARK_TOGGLE;

  const getCookieExpiry = () => {
    const today = new Date();
    return new Date(today.getFullYear(), today.getMonth(), today.getDate() + themeCookieExpiry);
  };

  const getCookieOptions = () => {
    const serverURL = new URL(getConfig().LMS_BASE_URL);
    const options = { domain: serverURL.hostname, path: '/', expires: getCookieExpiry() };
    return options;
  };

  const addDarkThemeToIframes = () => {
    const iframes = document.getElementsByTagName('iframe');
    const iframesLength = iframes.length;
    if (iframesLength > 0) {
      Array.from({ length: iframesLength }).forEach((_, index) => {
        const style = document.createElement('style');
        style.textContent = `
          body{
            background-color: #0D0D0E;
            color: #ccc;
          }
          a {color: #ccc;}
          a:hover{color: #d3d3d3;}
          `;
        if (iframes[index].contentDocument) { iframes[index].contentDocument.head.appendChild(style); }
      });
    }
  };

  useEffect(() => {
    const theme = cookies.get(themeCookie);

    // - When page loads, Footer loads before MFE content. Since there is no iframe on page,
    // it does not append any class. MutationObserver observes changes in DOM and hence appends dark
    // attributes when iframe is added. After 15 sec, this observer is destroyed to conserve resources. 
    // - It has been added outside dark-theme condition so that it can be removed on Component Unmount.
    // - Observer can be passed to `addDarkThemeToIframes` function and disconnected after observing Iframe.
    // This approach has a limitation: the observer first detects the iframe and then detects the docSrc. 
    // We need to wait for docSrc to fully load before appending the style tag.
    const observer = new MutationObserver(() => {
      addDarkThemeToIframes();
    });

    if (isThemeToggleEnabled && theme === 'dark') {
      document.body.classList.add('indigo-dark-theme');
      
      observer.observe(document.body, { childList: true, subtree: true });
      setTimeout(() => observer?.disconnect(), 15000); // clear after 15 sec to avoid resource usage

      cookies.set(themeCookie, theme, getCookieOptions());      //  on page load, update expiry
    }

    return () => observer?.disconnect();
  }, []);

  return (<div />);
};

async function setConfig () {
  let config = {
    pluginSlots: {}
  };

  try {
    /* We can't assume FPF exists, as it's not declared as a dependency in all
     * MFEs, so we import it dynamically. In addition, for dynamic imports to
     * work with Webpack all of the code that actually uses the imported module
     * needs to be inside the `try{}` block.
     */
    const { DIRECT_PLUGIN, PLUGIN_OPERATIONS } = await import('@openedx/frontend-plugin-framework');const IndigoFooter = () => {
  const intl = useIntl();
  const config = getConfig();

  const indigoFooterNavLinks = config.INDIGO_FOOTER_NAV_LINKS || [];

  const messages = {
    "footer.poweredby.text": {
      id: "footer.poweredby.text",
      defaultMessage: "Powered by",
      description: "text for the footer",
    },
    "footer.tutorlogo.altText": {
      id: "footer.tutorlogo.altText",
      defaultMessage: "Runs on Tutor",
      description: "alt text for the footer tutor logo",
    },
    "footer.logo.altText": {
      id: "footer.logo.altText",
      defaultMessage: "Powered by Open edX",
      description: "alt text for the footer logo.",
    },
    "footer.copyright.text": {
      id: "footer.copyright.text",
      defaultMessage: `Copyrights ©${new Date().getFullYear()}. All Rights Reserved.`,
      description: "copyright text for the footer",
    },
  };

  return (
    <div className="wrapper wrapper-footer">
      <footer id="footer" className="tutor-container">
        <div className="footer-top">
          <div className="powered-area">
            <ul className="logo-list">
              <li>{intl.formatMessage(messages["footer.poweredby.text"])}</li>
              <li>
                <a
                  href="https://edly.io/tutor/"
                  rel="noreferrer"
                  target="_blank"
                >
                  <img
                    src={`${config.LMS_BASE_URL}/theming/asset/images/tutor-logo.png`}
                    alt={intl.formatMessage(
                      messages["footer.tutorlogo.altText"]
                    )}
                    width="57"
                  />
                </a>
              </li>
              <li>
                <a href="https://open.edx.org" rel="noreferrer" target="_blank">
                  <img
                    src={`${config.LMS_BASE_URL}/theming/asset/images/openedx-logo.png`}
                    alt={intl.formatMessage(messages["footer.logo.altText"])}
                    width="79"
                  />
                </a>
              </li>
            </ul>
          </div>
          <nav className="nav-colophon">
            <ol>
              {indigoFooterNavLinks.map((link) => (
                <li key={link.url}>
                  <a href={`${config.LMS_BASE_URL}${link.url}`}>{link.title}</a>
                </li>
              ))}
            </ol>
          </nav>
        </div>
        <span className="copyright-site">
          {intl.formatMessage(messages["footer.copyright.text"])}
        </span>
      </footer>
    </div>
  );
};

const ToggleThemeButton = () => {
  const intl = useIntl();
  const [isDarkThemeEnabled, setIsDarkThemeEnabled] = useState(false);

  const themeCookie = "indigo-toggle-dark";
  const themeCookieExpiry = 90; // days
  const isThemeToggleEnabled = getConfig().INDIGO_ENABLE_DARK_TOGGLE;

  const getCookie = (name) => {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith(name + "="))
      ?.split("=")[1];
  };

  const setCookie = (name, value, { domain, path, expires }) => {
    document.cookie = `${name}=${value}; domain=${domain}; path=${path}; expires=${expires.toUTCString()}; SameSite=Lax`;
  };

  const getCookieExpiry = () => {
    const today = new Date();
    return new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() + themeCookieExpiry
    );
  };

  const getCookieOptions = (serverURL) => ({
    domain: serverURL.hostname,
    path: "/",
    expires: getCookieExpiry(),
  });

  const addDarkThemeToIframes = () => {
    const iframes = document.getElementsByTagName("iframe");
    const iframesLength = iframes.length;
    if (iframesLength > 0) {
      Array.from({ length: iframesLength }).forEach((_, ind) => {
        const style = document.createElement("style");
        style.textContent = `
          body{
            background-color: #0D0D0E;
            color: #ccc;
          }
          a {color: #ccc;}
          a:hover{color: #d3d3d3;}
          `;
        if (iframes[ind].contentDocument) {
          iframes[ind].contentDocument.head.appendChild(style);
        }
      });
    }
  };

  const removeDarkThemeFromiframes = () => {
    const iframes = document.getElementsByTagName("iframe");
    const iframesLength = iframes.length;

    Array.from({ length: iframesLength }).forEach((_, ind) => {
      if (iframes[ind].contentDocument) {
        const iframeHead = iframes[ind].contentDocument.head;
        const styleTag = Array.from(iframeHead.querySelectorAll("style")).find(
          (style) =>
            style.textContent.includes("background-color: #0D0D0E;") &&
            style.textContent.includes("color: #ccc;")
        );
        if (styleTag) {
          styleTag.remove();
        }
      }
    });
  };

  const onToggleTheme = () => {
    const serverURL = new URL(getConfig().LMS_BASE_URL);
    let theme = "";

    if (getCookie(themeCookie) === "dark") {
      document.body.classList.remove("indigo-dark-theme");
      removeDarkThemeFromiframes();
      setIsDarkThemeEnabled(false);
      theme = "light";
    } else {
      document.body.classList.add("indigo-dark-theme");
      addDarkThemeToIframes();
      setIsDarkThemeEnabled(true);
      theme = "dark";
    }
    setCookie(themeCookie, theme, getCookieOptions(serverURL));

    const learningMFEUnitIframe = document.getElementById("unit-iframe");
    if (learningMFEUnitIframe) {
      learningMFEUnitIframe.contentWindow.postMessage(
        { "indigo-toggle-dark": theme },
        serverURL.origin
      );
    }
  };

  const hanldeKeyUp = (event) => {
    if (event.key === "Enter") {
      onToggleTheme();
    }
  };

  if (!isThemeToggleEnabled) {
    return <div />;
  }

  const messages = {
    "header.user.theme": {
      id: "header.user.theme",
      defaultMessage: "Toggle Theme",
      description: "Toggle between light and dark theme",
    },
  };

  return (
    <div className="theme-toggle-button mr-3">
      <div className="light-theme-icon">
        <Icon src={WbSunny} />
      </div>
      <div className="toggle-switch">
        <label htmlFor="theme-toggle-checkbox" className="switch">
          <input
            id="theme-toggle-checkbox"
            defaultChecked={getCookie(themeCookie) === "dark"}
            onChange={onToggleTheme}
            onKeyUp={hanldeKeyUp}
            type="checkbox"
            title={intl.formatMessage(messages["header.user.theme"])}
          />
          <span className="slider round" />
          <span id="theme-label" className="sr-only">{`Switch to ${
            isDarkThemeEnabled ? "Light" : "Dark"
          } Mode`}</span>
        </label>
      </div>
      <div className="dark-theme-icon">
        <Icon src={Nightlight} />
      </div>
    </div>
  );
};

const MobileViewHeader = () => {
  const config = getConfig();
  const intl = useIntl();
  const messages = {
    "mobile.view.header.logo.altText": {
      id: "mobile.view.header.logo.altText",
      defaultMessage: "My Open edX",
      description: "Mobile view header logo altText",
    },
  };
  return (
    <div className="container-xl py-2 d-flex align-items-center justify-content-between">
      <a
        className="logo"
        href={`${config.LMS_BASE_URL}/dashboard`}
        style={Object.assign({}, { display: "flex", alignItems: "center" })}
      >
        <img
          className="d-block"
          src={`${config.LMS_BASE_URL}/theming/asset/images/logo.png`}
          alt={intl.formatMessage(messages["mobile.view.header.logo.altText"])}
          height={21}
        />
      </a>
      <ToggleThemeButton />
    </div>
  );
};
    if (process.env.APP_ID == 'admin-console') {
    }
    if (process.env.APP_ID == 'authn') {
    }
    if (process.env.APP_ID == 'authoring') {
    }
    if (process.env.APP_ID == 'account') {
      addPlugins(config, 'org.openedx.frontend.layout.footer.v1', [ 
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
  ]);
      addPlugins(config, 'desktop_secondary_menu_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: ToggleThemeButton,
                    },
                },
        ]);
      addPlugins(config, 'mobile_header_slot', [
                {
                    op: PLUGIN_OPERATIONS.Hide,
                    widgetId: 'default_contents',
                }
                ]);
      addPlugins(config, 'mobile_header_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: MobileViewHeader,
                    },
                },
                ]);
    }
    if (process.env.APP_ID == 'communications') {
    }
    if (process.env.APP_ID == 'discussions') {
      addPlugins(config, 'org.openedx.frontend.layout.footer.v1', [ 
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
  ]);
      addPlugins(config, 'desktop_secondary_menu_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: ToggleThemeButton,
                    },
                },
        ]);
      addPlugins(config, 'mobile_header_slot', [
                {
                    op: PLUGIN_OPERATIONS.Hide,
                    widgetId: 'default_contents',
                }
                ]);
      addPlugins(config, 'mobile_header_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: MobileViewHeader,
                    },
                },
                ]);
    }
    if (process.env.APP_ID == 'gradebook') {
    }
    if (process.env.APP_ID == 'learner-dashboard') {
      addPlugins(config, 'org.openedx.frontend.layout.footer.v1', [ 
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
  ]);
      addPlugins(config, 'desktop_secondary_menu_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: ToggleThemeButton,
                    },
                },
        ]);
      addPlugins(config, 'mobile_header_slot', [
                {
                    op: PLUGIN_OPERATIONS.Hide,
                    widgetId: 'default_contents',
                }
                ]);
      addPlugins(config, 'mobile_header_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: MobileViewHeader,
                    },
                },
                ]);
    }
    if (process.env.APP_ID == 'learning') {
      addPlugins(config, 'org.openedx.frontend.layout.footer.v1', [ 
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
  ]);
      addPlugins(config, 'learning_help_slot', [
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        }
        ]);
      addPlugins(config, 'learning_help_slot', [ 
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'theme_switch_button',
                type: DIRECT_PLUGIN,
                RenderWidget: ToggleThemeButton,
            },
        },
        ]);
    }
    if (process.env.APP_ID == 'ora-grading') {
    }
    if (process.env.APP_ID == 'profile') {
      addPlugins(config, 'org.openedx.frontend.layout.footer.v1', [ 
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
  ]);
      addPlugins(config, 'desktop_secondary_menu_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: ToggleThemeButton,
                    },
                },
        ]);
      addPlugins(config, 'mobile_header_slot', [
                {
                    op: PLUGIN_OPERATIONS.Hide,
                    widgetId: 'default_contents',
                }
                ]);
      addPlugins(config, 'mobile_header_slot', [ 
                {
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {
                        id: 'theme_switch_button',
                        type: DIRECT_PLUGIN,
                        RenderWidget: MobileViewHeader,
                    },
                },
                ]);
    }
  } catch (err) { console.error("env.config.jsx failed to apply: ", err);}

  return config;
}

export default setConfig;