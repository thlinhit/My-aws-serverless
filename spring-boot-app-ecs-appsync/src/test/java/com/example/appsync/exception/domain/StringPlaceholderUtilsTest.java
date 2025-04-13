package com.example.appsync.exception.domain;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;

import java.util.List;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for StringPlaceholderUtils
 */
class StringPlaceholderUtilsTest {

    @Test
    void format_NullTemplate_ReturnsNull() {
        // When
        String result = StringPlaceholderUtils.format(null, "value");
        
        // Then
        assertThat(result).isNull();
    }
    
    @ParameterizedTest
    @NullAndEmptySource
    void format_TemplateWithoutPlaceholders_ReturnsOriginalTemplate(String args) {
        // Given
        String template = "This is a string without placeholders";
        
        // When
        String result = StringPlaceholderUtils.format(template, (Object) args);
        
        // Then
        assertThat(result).isEqualTo(template);
    }
    
    @Test
    void format_NullArgs_ReturnsOriginalTemplate() {
        // Given
        String template = "Hello, ${name}!";
        
        // When
        String result = StringPlaceholderUtils.format(template, (Object[]) null);
        
        // Then
        assertThat(result).isEqualTo(template);
    }
    
    @Test
    void format_EmptyArgs_ReturnsOriginalTemplate() {
        // Given
        String template = "Hello, ${name}!";
        
        // When
        String result = StringPlaceholderUtils.format(template);
        
        // Then
        assertThat(result).isEqualTo(template);
    }
    
    @Test
    void format_SinglePlaceholder_ReturnsFormattedString() {
        // Given
        String template = "Hello, ${name}!";
        
        // When
        String result = StringPlaceholderUtils.format(template, "John");
        
        // Then
        assertThat(result).isEqualTo("Hello, John!");
    }
    
    @Test
    void format_MultiplePlaceholders_ReturnsFormattedString() {
        // Given
        String template = "Hello, ${firstName} ${lastName}!";
        
        // When
        String result = StringPlaceholderUtils.format(template, "John", "Doe");
        
        // Then
        assertThat(result).isEqualTo("Hello, John Doe!");
    }
    
    @Test
    void format_RepeatedPlaceholder_ReplacesAllOccurrences() {
        // Given
        String template = "Hello, ${name}! How are you, ${name}?";
        
        // When
        String result = StringPlaceholderUtils.format(template, "John");
        
        // Then
        assertThat(result).isEqualTo("Hello, John! How are you, John?");
    }
    
    @Test
    void format_MorePlaceholdersThanArgs_LeavesExtraPlaceholdersUnchanged() {
        // Given
        String template = "Hello, ${firstName} ${lastName}!";
        
        // When
        String result = StringPlaceholderUtils.format(template, "John");
        
        // Then
        assertThat(result).isEqualTo("Hello, John ${lastName}!");
    }
    
    @Test
    void format_MoreArgsThanPlaceholders_IgnoresExtraArgs() {
        // Given
        String template = "Hello, ${name}!";
        
        // When
        String result = StringPlaceholderUtils.format(template, "John", "Doe", "Smith");
        
        // Then
        assertThat(result).isEqualTo("Hello, John!");
    }
    
    @Test
    void format_NullArgValue_ReplacesWithNullString() {
        // Given
        String template = "Value is: ${value}";
        
        // When
        String result = StringPlaceholderUtils.format(template, (Object) null);
        
        // Then
        assertThat(result).isEqualTo("Value is: null");
    }
    
    @Test
    void format_NonStringArgs_ConvertsToString() {
        // Given
        String template = "Number: ${number}, Boolean: ${boolean}, Object: ${object}";
        
        // When
        String result = StringPlaceholderUtils.format(template, 42, true, new TestObject("test"));
        
        // Then
        assertThat(result).isEqualTo("Number: 42, Boolean: true, Object: TestObject(test)");
    }
    
    @Test
    void getPlaceholders_NullTemplate_ReturnsEmptyList() {
        // When
        List<String> placeholders = StringPlaceholderUtils.getPlaceholders(null);
        
        // Then
        assertThat(placeholders).isEmpty();
    }
    
    @Test
    void getPlaceholders_TemplateWithoutPlaceholders_ReturnsEmptyList() {
        // Given
        String template = "This is a string without placeholders";
        
        // When
        List<String> placeholders = StringPlaceholderUtils.getPlaceholders(template);
        
        // Then
        assertThat(placeholders).isEmpty();
    }
    
    @ParameterizedTest
    @MethodSource("placeholderTemplates")
    void getPlaceholders_TemplateWithPlaceholders_ReturnsPlaceholderNames(
            String template, List<String> expectedPlaceholders) {
        // When
        List<String> placeholders = StringPlaceholderUtils.getPlaceholders(template);
        
        // Then
        assertThat(placeholders).isEqualTo(expectedPlaceholders);
    }
    
    @Test
    void getPlaceholders_ComplexTemplate_ReturnsAllPlaceholders() {
        // Given
        String template = "Hello, ${firstName} ${lastName}! Your ID is ${id} and your role is ${role}";
        
        // When
        List<String> placeholders = StringPlaceholderUtils.getPlaceholders(template);
        
        // Then
        assertThat(placeholders).containsExactly("firstName", "lastName", "id", "role");
    }

    private static Stream<Arguments> placeholderTemplates() {
        return Stream.of(
                Arguments.of("Hello, ${name}!", List.of("name")),
                Arguments.of("Hello, ${firstName} ${lastName}!", List.of("firstName", "lastName")),
                Arguments.of("${greeting}, ${name}!", List.of("greeting", "name")),
                Arguments.of("No ${placeholder1} at the ${placeholder2}", List.of("placeholder1", "placeholder2")),
                Arguments.of("${placeholder} at the beginning", List.of("placeholder")),
                Arguments.of("At the end ${placeholder}", List.of("placeholder")),
                Arguments.of("Same ${placeholder} twice ${placeholder}", List.of("placeholder", "placeholder"))
        );
    }
    
    // Helper class for testing non-String objects
    private static class TestObject {
        private final String value;
        
        public TestObject(String value) {
            this.value = value;
        }
        
        @Override
        public String toString() {
            return "TestObject(" + value + ")";
        }
    }
} 