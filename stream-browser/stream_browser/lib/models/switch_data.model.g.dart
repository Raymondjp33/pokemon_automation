// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'switch_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SwitchData _$SwitchDataFromJson(Map<String, dynamic> json) => SwitchData(
      pokemon: (json['pokemon'] as List<dynamic>)
          .map((e) => PokemonData.fromJson(e as Map<String, dynamic>?))
          .toList(),
    );

Map<String, dynamic> _$SwitchDataToJson(SwitchData instance) =>
    <String, dynamic>{
      'pokemon': instance.pokemon.map((e) => e.toJson()).toList(),
    };
