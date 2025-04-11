package com.example.appsync.exception.domain;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Utility class for handling string placeholders in error messages
 */
public class StringPlaceholderUtils {
    private static final Pattern PLACEHOLDER_PATTERN = Pattern.compile("\\$\\{([^}]+)\\}");

    /**
     * Formats a template string by replacing placeholders with provided values
     *
     * @param template The template string with placeholders like ${name}
     * @param args The values to replace placeholders with
     * @return The formatted string
     */
    public static String format(String template, Object... args) {
        if (template == null) {
            return null;
        }

        List<String> placeholders = getPlaceholders(template);
        if (placeholders.isEmpty() || args == null || args.length == 0) {
            return template;
        }

        String result = template;
        for (int i = 0; i < placeholders.size() && i < args.length; i++) {
            String placeholder = placeholders.get(i);
            Object value = args[i];
            result = result.replace("${" + placeholder + "}", value != null ? value.toString() : "null");
        }

        return result;
    }

    /**
     * Extracts placeholders from a template string
     *
     * @param template The template string
     * @return List of placeholder names without ${} syntax
     */
    public static List<String> getPlaceholders(String template) {
        List<String> placeholders = new ArrayList<>();
        if (template == null) {
            return placeholders;
        }

        Matcher matcher = PLACEHOLDER_PATTERN.matcher(template);
        while (matcher.find()) {
            placeholders.add(matcher.group(1));
        }

        return placeholders;
    }
} 