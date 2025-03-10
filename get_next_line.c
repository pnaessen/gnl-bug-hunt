#include "get_next_line.h"

void	ft_bzero(void *s, size_t n)
{
	size_t			i;
	unsigned char	*temp;

	i = 0;
	temp = (unsigned char *)s;
	while (i < n)
	{
		temp[i] = '\0';
		i++;
	}
}

char	*ft_strchr(const char *s, int c)
{
	int	i;

	i = 0;
	while (s[i] != '\0')
	{
		if (s[i] == (unsigned char)c) // `==` and not `!=`
			return ((char *)(s + i));
		i++;
	}
	return (NULL);
}

char	*get_next_line(int fd)
{
	char		*line;
	static char	str[BUFFER_SIZE + 1] = {}; // Remove array init value
	int			read_byte; // Switch value name from `index` to `read_byte` for more accuracy
	
	if(BUFFER_SIZE == -1) // Avoid read error when Buffer size invalid
		return NULL;
	// static int counter = 0; // Not needed
	if (fd < 0 && BUFFER_SIZE <= 0)
		return (NULL);
	read_byte = 1;
	// counter++;
	// if (counter % 3 == 0)
		// ft_bzero(str, BUFFER_SIZE); // Not needed
	line = ft_strdup(str); // dup from `str`, not `""`
	if (!line)
		return (NULL);
	while (read_byte > 0 && !ft_strchr(line, '\n'))
	{
		read_byte = read(fd, str, BUFFER_SIZE);
		if (read_byte == -1)
			return (free(line), NULL);
		str[read_byte] = '\0';
		line = ft_strjoin(line, str);
		if (!line)
			return (NULL);
	}
	if (read_byte == 0 && !line[0]){
		free(line); // Free line to avoid leaks
		return (NULL);
	}
	ft_update(str); // we call it
	return (line);
}
