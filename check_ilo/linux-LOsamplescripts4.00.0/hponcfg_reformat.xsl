<?xml version="1.0"?>

<!--         RIBCL Sample Script for HP Lights-Out Products                               -->
<!--   Copyright (c) 2012 Hewlett-Packard Development Company, L.P.                       -->
<!--                                                                                      -->
<!-- Steps to be followed to capture and restore the configuration using "hponcfg".       -->
<!-- 1. On Windows                                                                        -->
<!--    a. Run "hponcfg -f hponcfgcap.xml -l log.xml".                                    -->
<!--       This captures the current iLO configuration in the XML file "log.xml".         -->
<!--    b. Include <RIBCL> and </RIBCL> tags. The whole xml data need to be included      -->
<!--       between these RIBCL tags.                                                      -->
<!--    c. Run "msxsl log.xml hponcfg_reformat.xsl -o hponcfg_settings_msxsl_ouput.xml"   -->
<!--	   This will store the reformatted XML output in the XML file 			      -->
<!--	   "hponcfg_settings_msxsl_ouput.xml"  based on the provided input XSL script       -->
<!--	   "hponcfg_reformat.xsl" and input XML file "log.xml".                             -->
<!--       nxslt2 (version 2.2 onwards) can also be used instead of msxsl. 		      -->
<!--                                                                                      -->
<!--    To Restore the iLO configuration:                                                 -->
<!--       Run "hponcfg -f hponcfg_settings_msxsl_ouput.xml".                             -->
<!--       This restores the current iLO configuration to the data which was captured     -->
<!--       under "Step a".                                                                -->
<!--                                                                                      -->
<!-- 2. On Linux                                                                          -->
<!--    a. Run "hponcfg -f hponcfgcap.xml -l log.xml"                                     -->
<!--       This captures the current iLO configuration in the XML file "log.xml".         -->
<!--    b. Include <RIBCL> and </RIBCL> tags. The whole xml data need to be included      -->
<!--       between these RIBCL tags.                                                      -->
<!--    c. Run "xsltproc -o hponcfg_settings_reformated.xml hponcfg_reformat.xsl log.xml" -->
<!--       This will store the reformatted XML output in the XML file                     -->
<!--       "hponcfg_settings_reformated.xml" based on the provided input xsl script       -->
<!--       "hponcfg_reformat.xsl" and  XML input "log.xml".                               -->

<!--    To Restore the iLO configuration:                                                 -->
<!--       Run "hponcfg -f hponcfg_settings_reformated.xml"                               -->
<!--       This restores the current iLO configuration to the data which was captured.    -->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" omit-xml-declaration="yes" indent="yes" encoding="ascii"/>

	<!-- copy everything -->
	<xsl:template match="node()|@*">
		<xsl:copy>
			<xsl:apply-templates select="@*"/>
			<xsl:apply-templates/>
		</xsl:copy>
	</xsl:template>
	
	<!-- replace empty nodes with nothing, Optional but cleaner -->
	<xsl:template match="//node()[.='']">
		<xsl:copy-of select="."/>
	</xsl:template>

	<!-- Introduce LOGIN tag -->
	<xsl:template match="/RIBCL">
		<RIBCL VERSION="2.0">
		   <LOGIN USER_LOGIN="admin" PASSWORD="password">
			<xsl:apply-templates select="child::node()"/>
		   </LOGIN>
		</RIBCL>
	</xsl:template>
	
	<!-- create subsections -->
	<xsl:template match="/RIBCL/GET_DIR_CONFIG">
		<DIR_INFO mode="write">
		  <MOD_DIR_CONFIG>
		  	<xsl:apply-templates select="child::node()"/>
		  </MOD_DIR_CONFIG>
		</DIR_INFO>
	</xsl:template>

	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS">
		<RIB_INFO mode="write">
		  <MOD_NETWORK_SETTINGS>
				<xsl:apply-templates select="child::node()"/>
		  </MOD_NETWORK_SETTINGS>
		</RIB_INFO>
	</xsl:template>

	<xsl:template match="/RIBCL/GET_ALL_USER_INFO">
		<USER_INFO mode="write">
			<xsl:apply-templates/>
		</USER_INFO>
	</xsl:template>

	<xsl:template match="/RIBCL/GET_ALL_USER_INFO/GET_USER">
		<ADD_USER USER_NAME="{@USER_NAME}"
			USER_LOGIN="{@USER_LOGIN}"
			PASSWORD= "%user_password%">
			<xsl:apply-templates select="@*[contains(name(.), 'PRIV')]"/>
		</ADD_USER>
	</xsl:template>

	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS">
		<RIB_INFO mode="write">
			<MOD_GLOBAL_SETTINGS>
				<xsl:apply-templates/>
			</MOD_GLOBAL_SETTINGS>
		</RIB_INFO>
	</xsl:template>

	<!-- don't set the GRPACCT NAME and VALUE if the NAME is NULL -->
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT1_NAME/@VALUE='']/DIR_GRPACCT1_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT1_PRIV/@VALUE='']/DIR_GRPACCT1_PRIV"/>
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT2_NAME/@VALUE='']/DIR_GRPACCT2_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT2_PRIV/@VALUE='']/DIR_GRPACCT2_PRIV"/>
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT3_NAME/@VALUE='']/DIR_GRPACCT3_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT3_PRIV/@VALUE='']/DIR_GRPACCT3_PRIV"/>
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT4_NAME/@VALUE='']/DIR_GRPACCT4_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT4_PRIV/@VALUE='']/DIR_GRPACCT4_PRIV"/>
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT5_NAME/@VALUE='']/DIR_GRPACCT5_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT5_PRIV/@VALUE='']/DIR_GRPACCT5_PRIV"/>
      <xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT6_NAME/@VALUE='']/DIR_GRPACCT6_NAME"/>
	<xsl:template match="/RIBCL/GET_DIR_CONFIG[DIR_GRPACCT6_PRIV/@VALUE='']/DIR_GRPACCT6_PRIV"/>


	<!-- don't set these, remove from output -->
	<!-- can't set MAC -->
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS/MAC_ADDRESS"/>
	<!-- don't set the VLAN ID if it is set to 0 -->
      <xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[SHARED_NETWORK_PORT_VLAN_ID/@VALUE='0']/SHARED_NETWORK_PORT_VLAN_ID"/>
	<!-- don't set IP, Gateway or DNS if DHCP is providing -->
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[DHCP_ENABLE/@VALUE='Y']/IP_ADDRESS"/>
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[DHCP_ENABLE/@VALUE='Y' and DHCP_GATEWAY/@VALUE='Y']/GATEWAY_IP_ADDRESS"/>
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[DHCP_ENABLE/@VALUE='Y' and DHCP_DNS_SERVER/@VALUE='Y']/PRIM_DNS_SERVER"/>
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[DHCP_ENABLE/@VALUE='Y' and DHCP_DNS_SERVER/@VALUE='Y']/SEC_DNS_SERVER"/>
	<xsl:template match="/RIBCL/GET_NETWORK_SETTINGS[DHCP_ENABLE/@VALUE='Y' and DHCP_DNS_SERVER/@VALUE='Y']/TER_DNS_SERVER"/>

	<!-- reformat privileges from ADMIN_PRIV="Y" to <ADMIN_PRIV value="Y"/> -->
	<xsl:template match="/RIBCL/GET_ALL_USER_INFO/GET_USER/@*[contains(name(.), 'PRIV')]">
		<xsl:element name="{name(.)}">
			<xsl:attribute name="value"><xsl:value-of select="."/></xsl:attribute>
		</xsl:element>
	</xsl:template>

	<!-- reformat global settings -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/SERIAL_CLI_STATUS">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">1</xsl:when>
					<xsl:when test="@VALUE='Enabled-No Authentication'">2</xsl:when>
					<xsl:when test="@VALUE='Enabled-Authentication Required'">3</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise> <!-- No change -->
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

	<!-- HIGH_PERFORMANCE_MOUSE -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/HIGH_PERFORMANCE_MOUSE">	                                                        
         <xsl:comment>
      NOTE: Hponcfg reports "script failed" when "HIGH_PERFORMANCE_MOUSE" setting is
            attempted under the following conditions:
            1. When iLO Remote Console is open.
            The error message displayed here will be "This setting cannot be changed
            while remote console is connected."
            2. When iLO Virtual Media is connected.
            The error message displayed will be "This setting can not be changed
            while virtual media is connected."
    </xsl:comment>
    <xsl:text>
    </xsl:text>

  	 <xsl:copy>
        	    <xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
					<xsl:when test="@VALUE='Automatic'">Automatic</xsl:when>
                    <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise> <!-- No change -->
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

      <!-- AUTHENTICATION_FAILURE_LOGGING  -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/AUTHENTICATION_FAILURE_LOGGING">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
                              <xsl:when test="@VALUE='Disabled'">0</xsl:when>
                              <xsl:when test="@VALUE='Enabled-every failure'">1</xsl:when>
                              <xsl:when test="@VALUE='Enabled-every 2nd failure'">2</xsl:when>
                              <xsl:when test="@VALUE='Enabled-every 3rd failure'">3</xsl:when>
                              <xsl:when test="@VALUE='Enabled-every 5th failure'">5</xsl:when>
                              <xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                              <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

    <!-- KEY_UP_KEY_DOWN  -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/KEY_UP_KEY_DOWN">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>
 
    <!-- CONSOLE_CAPTURE_ENABLE  -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/CONSOLE_CAPTURE_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

 <!-- CONSOLE_CAPTURE_BOOT_BUFFER_ENABLE -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/CONSOLE_CAPTURE_BOOT_BUFFER_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

<!-- CONSOLE_CAPTURE_FAULT_BUFFER_ENABLE -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/CONSOLE_CAPTURE_FAULT_BUFFER_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

<!-- INTERACTIVE_CONSOLE_REPLAY_ENABLE -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/INTERACTIVE_CONSOLE_REPLAY_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

<!-- CAPTURE_AUTO_EXPORT_ENABLE  -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/CAPTURE_AUTO_EXPORT_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

<!-- SHARED_CONSOLE_ENABLE  -->	
	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/SHARED_CONSOLE_ENABLE">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='Disabled'">N</xsl:when>
					<xsl:when test="@VALUE='Enabled'">Y</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

	<xsl:template match="/RIBCL/GET_GLOBAL_SETTINGS/SERIAL_CLI_SPEED">
		<xsl:copy>
			<xsl:attribute name="VALUE">
				<xsl:choose>
					<xsl:when test="@VALUE='9600'">1</xsl:when>
					<xsl:when test="@VALUE='19200'">2</xsl:when>
					<xsl:when test="@VALUE='38400'">3</xsl:when>
					<xsl:when test="@VALUE='57600'">4</xsl:when>
					<xsl:when test="@VALUE='115200'">5</xsl:when>
                                        <xsl:otherwise><xsl:value-of select="@VALUE"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>
