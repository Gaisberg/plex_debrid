import React, { useEffect, useState } from 'react';
import { Item } from '../types/Types';
import MediaItemsSearchBar from '../components/MediaItemsSearchBar';
import MediaItemsCard from '../components/MediaItemsCard';
import styles from '../components/MediaItems.module.css';

function MediaPage() {
  const [items, setItems] = useState([]);
  const [groupedItems, setGroupedItems] = useState({});
  const [searchTerm, setSearchTerm] = useState<string>('');


  const handleSearch = (query: string) => {
    setSearchTerm(query);
  };

  useEffect(() => {
    fetch('http://localhost:8080/items')
      .then(response => response.json())
      .then(data => {
        setItems(data);
        setGroupedItems(groupByState(data));
      });
  }, []);

  const groupByState = (items : any) => {
    return items.reduce((acc: any, item : any) => {
      if (!acc[item.state]) {
        acc[item.state] = [];
      }
      acc[item.state].push(item);
      return acc;
    }, {});
  };

  const states = [
    "ERROR",
    "UNKNOWN",
    "LIBRARY",
    "LIBRARY_METADATA",
    "CONTENT",
    "SCRAPED",
    "DOWNLOADING"
  ];

  return (
    <div>
    	<div className={styles.searchBarContainer}>
            <MediaItemsSearchBar onSearch={handleSearch} />
        </div>
        <div className={styles.cardContainer}>
            {states.map(state => {
                const filteredItems = (groupedItems as any)[state]?.filter(
                    (item: any) =>
                    item.title && item.title.toLowerCase().includes(searchTerm.toLowerCase())
                ) || [];
                return (
                <MediaItemsCard
                    key={state}
                    title={state}
                    items={filteredItems}
                />
                );
            })}
      </div>
    </div>
  );
}

export default MediaPage;
