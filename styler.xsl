<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="no" />
  <!-- Select which attributes to transform -->
  <xsl:variable name="selected" select="tokenize('stop-color stop-opacity opacity fill', '\s+')" />
  <!-- Transformation  -->
  <xsl:template match="*">
    <!-- Copy the element -->
    <xsl:element name="{name()}">
      <!-- Gather selected attributes -->
      <xsl:variable name="style">
        <xsl:for-each select="@*[index-of($selected, name(.)) != 0]">
            <xsl:value-of select="concat(name(.), ':', .)"/>
            <xsl:if test="not(last() = position())">
              <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <!-- Copy other attributes -->
      <xsl:for-each select="@*[not(index-of($selected, name(.)))]">
        <xsl:copy/>
      </xsl:for-each>
      <!-- Add style, if needed -->
      <xsl:if test="string-length($style)">
        <xsl:attribute name="style"><xsl:value-of select="$style"/></xsl:attribute>
      </xsl:if>
      <!-- Apply recursively -->
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
